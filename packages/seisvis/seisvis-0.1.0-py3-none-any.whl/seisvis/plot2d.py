# Copyright (c) 2025 Qi Pang.
# GeoAI-INV, Xi'an Jiaotong University (XJTU).
# All rights reserved.
import matplotlib.pyplot as plt
from typing import Optional, Union, Tuple, List, Dict
import numpy as np
import itertools
from scipy.interpolate import interp1d

from .plot_config import PlotConfig
from .data_config import DataCube

ClipType = Union[str, Tuple[float, float], None]
SeismicType = Dict[str, Union[str, ClipType]]
#  {'type': 'deg10','cmap': 'gray','clip': None}  # or 'rubust' or (min, max)

class Seis2DPlotter:
    """2D data plotter"""
    
    def __init__(self, data_cube: Union[DataCube],size=None,
                       config: Optional[PlotConfig] = None):
        """
        size: [il_start, il_end, xl_start, xl_end, t_end, t_start]
        """
        self.config = config or PlotConfig()
        self.config.apply_matplotlib_settings()
        
        self.cube = data_cube
        self.size = size 
        
    @property
    def shape(self):
        if self.size is None:
            raise ValueError("shape requires 3D data. 'size' is not defined.")
        return [
            self.size[1] - self.size[0] + 1,
            self.size[3] - self.size[2] + 1,
            self.size[4] - self.size[5] + 1,
        ]

    @property
    def extent_inline_2d(self):
        if self.size is None:
            raise ValueError("extent_inline_2d requires 3D data. 'size' is not defined.")
        return [self.size[2], self.size[3], self.size[4], self.size[5]]

    @property
    def extent_xline_2d(self):
        if self.size is None:
            raise ValueError("extent_xline_2d requires 3D data. 'size' is not defined.")
        return [self.size[0], self.size[1], self.size[4], self.size[5]]

    @property
    def extent_surface(self):
        if self.size is None:
            raise ValueError("extent_surface requires 3D data. 'size' is not defined.")
        return [self.size[2], self.size[3], self.size[0], self.size[1]]

        
    def _get_clip_values(self, array: np.ndarray, 
                        clip: Optional[Union[Tuple[float, float], str]] = None) -> Tuple[float, float]:
        """Calculate data clipping range with various methods"""
        if clip is None:
            return array.min(), array.max()
        elif isinstance(clip, str):
            if clip == 'robust':
                # Robust clipping using IQR
                q25, q75 = np.percentile(array, [25, 75])
                iqr = q75 - q25
                return q25 - 1.5*iqr, q75 + 1.5*iqr                
            else:
                raise ValueError(f"Unsupported clip type: {clip}")
        else:
            return float(clip[0]), float(clip[1])
        
    def _make_surface(self, raw_surface):
        
        surface_shape = self.shape[:2]
        full_surface = np.full(surface_shape, np.nan, dtype=np.float32)
        ils = np.arange(self.size[0], self.size[1]+1, 1, dtype=int)
        xls = np.arange(self.size[2], self.size[3]+1, 1, dtype=int)
        
        for idx, inline in enumerate(ils):
            x = raw_surface.loc[raw_surface.X == inline].Y 
            y = raw_surface.loc[raw_surface.X == inline].Z
            interp = interp1d(x, y, bounds_error=False, fill_value='extrapolate')
            full_surface[idx, :] = interp(xls) # (inline, crossline)
            
        return full_surface
    
    def _calculate_mask_from_horizons(self, top_h, base_h, dt=1):
        top_s = self._make_surface(top_h)
        base_s = self._make_surface(base_h)
        mask = np.zeros(self.shape, dtype=bool)  
    
        for i in range(mask.shape[0]):
            tss = (top_s[i, :] - self.size[5]) // dt
            mas = (base_s[i, :] - self.size[5]) // dt
            for j in range(len(tss)):
                start = int(tss[j])
                end = int(mas[j])
                if start < end:
                    mask[i, j, start:end] = True
                else:
                    mask[i, j, end:start] = True
        return mask
        
    def plot_surface(self, surface: np.ndarray, 
                    figsize: Tuple[int, int] = (7, 5),
                    cmap: str = 'viridis',
                    clip: Optional[Union[Tuple[float, float], str]] = None,
                    labels: Optional[Tuple[str, str]] = ('X', 'Y'),
                    title: Optional[str] = None,
                    extent: Optional[Tuple[float, float, float, float]] = None,
                    well_positions: Optional[Tuple[np.ndarray, np.ndarray]] = None,
                    contour_levels: int = 40) -> None:
 
        if surface.ndim != 2:
            raise ValueError("Surface data must be 2D")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        vmin, vmax = self._calculate_clip_values(surface, clip)
        

        c = ax.imshow(surface, aspect='auto', cmap=self.config.get_cmap(cmap), extent=extent,
                     vmin=vmin, vmax=vmax, origin='upper')
        

        ax.contour(surface, colors='k', levels=contour_levels, linewidths=0.5,
                  extent=extent, origin='upper')        

        if well_positions is not None:
            inline_coords, xline_coords = well_positions
            ax.scatter(xline_coords, inline_coords, color='k', s=50, marker='v',
                      edgecolors='white', linewidths=1, label='Well')
            ax.legend()        

        fig.colorbar(c, ax=ax, aspect=30, shrink=1.0, pad=0.01)
        
        if labels is not None:
            ax.set_xlabel(labels[0], **self.config.label_style)
            ax.set_ylabel(labels[1], **self.config.label_style)
        
        if title:
            ax.set_title(title, **self.config.title_style)
        
        plt.tight_layout()
        plt.show()
                
        
    def _extract_slice(self, section_idx, section_type, il_start, xl_start):
        
        if section_type == 'inline':
            assert il_start is not None, "You must provide il_start for inline section."
            il_idx = section_idx - il_start
            slice_2d_func = lambda cube: cube[il_idx, :, :].T
            horizon_filter = lambda df: df.loc[df.X == section_idx]
            x_label = "Crossline"
            title = f"Inline {section_idx}"
            extent = self.extent_inline_2d
        elif section_type == 'xline':
            assert xl_start is not None, "You must provide xl_start for crossline section."
            xl_idx = section_idx - xl_start
            slice_2d_func = lambda cube: cube[:, xl_idx, :].T
            horizon_filter = lambda df: df.loc[df.Y == section_idx]
            x_label = "Inline"
            title = f"Crossline {section_idx}"
            extent = self.extent_xline_2d
        else:
            raise ValueError("section_type must be 'inline' or 'xline'")
        
        return slice_2d_func, horizon_filter, x_label, title, extent    
               
    def plot_section(self, 
        section_idx=None,
        section_type='inline',
        show_seismic_type: Optional[SeismicType] = None,
        show_properties_type: Optional[SeismicType] = None,
        show_horizons_type: Optional[SeismicType] = None,
        show_wells_type: Optional[SeismicType] = None,
        t_axis_label="Time (ms)",
        unit_label_p = None, # 'g/cm³·m/s'
        figsize: Tuple[int, int] = (10, 4),
        save_path=None,  
        **kwargs
    ):  
        "This function requires 3D input data"
        fig, ax = plt.subplots(figsize=figsize)
        
        slice_2d_func, horizon_filter, x_label, title, extent = self._extract_slice(section_idx, section_type, 
                                                                            self.size[0], self.size[2])
        
        if show_seismic_type is not None:
            seis = self.cube.get('seismic', show_seismic_type['type'])
            seis_clip = self._get_clip_values(seis, show_seismic_type['clip'])
            
            if show_seismic_type['mask'] and show_horizons_type is not None  \
            and len(show_horizons_type['type'])>1:
                # print('yes')
                top_h =  self.cube.get('horizons', show_horizons_type['type'][0])
                base_h = self.cube.get('horizons', show_horizons_type['type'][-1])
                mask = self._calculate_mask_from_horizons(top_h, base_h)
                seis = seis * mask
            
            seis_sliced = slice_2d_func(seis)
            cmap = self.config.get_cmap(show_seismic_type['cmap']).copy()
            cmap.set_bad('white', alpha=0)
            
            seis_sliced = slice_2d_func(seis)
            c1 = ax.imshow(seis_sliced, aspect='auto', cmap=cmap,
                      vmin=seis_clip[0], vmax=seis_clip[1],
                      extent=extent, origin='upper', **kwargs)
            
        if show_properties_type is not None:
            prop = self.cube.get('properties', show_properties_type['type'])            
            prop_clip = self._get_clip_values(prop, show_properties_type['clip'])  
            
            if show_properties_type['mask'] and show_horizons_type is not None \
            and len(show_horizons_type['type'])>1:
                # print('yes')
                top_h =  self.cube.get('horizons', show_horizons_type['type'][0])
                base_h = self.cube.get('horizons', show_horizons_type['type'][-1])
                mask = self._calculate_mask_from_horizons(top_h, base_h)
                prop = np.ma.array(prop, mask=~mask)
                
                
            prop_sliced = slice_2d_func(prop)
            # Note:
            # Some issues may occur when using OpenDtect-style colormaps with masked data.
            # In particular, matplotlib may not handle 'set_bad()' correctly with certain custom colormaps,
            # resulting in masked (e.g., NaN) regions not being shown as transparent or white.
            # use Ture or False
            cmap = self.config.get_cmap(show_properties_type['cmap']).copy()
            cmap.set_bad('white', alpha=0)
            
            c2 = ax.imshow(prop_sliced, aspect='auto', cmap=cmap,
                      vmin=prop_clip[0], vmax=prop_clip[1],
                      extent=extent, origin='upper', **kwargs)
            
        if show_horizons_type is not None:
            hor = self.cube.get('horizons', show_horizons_type['type'])
            color_iter = itertools.cycle(['lime', 'magenta', 'blue', 'cyan', 'orange', 'yellow', 'red'])
            for name, df in hor.items():
                df_filtered = horizon_filter(df)
                if not df_filtered.empty:
                    x_vals = df_filtered.Y if section_type == 'inline' else df_filtered.X
                    z_vals = df_filtered.Z
                    ax.plot(x_vals, z_vals, lw=2.5, label=name, color=next(color_iter))
                    ax.legend(fontsize=self.config.legend_fontsize)
                
        if show_wells_type is not None:
            well_cmap = show_wells_type['cmap']
            well_width = show_wells_type['width'] or 4
            all_log_df = []
            for well in self.cube.data['wells'].values():
                all_log_df.append(well.get('log'))
            combined_log = np.concatenate(all_log_df)
            if show_properties_type is not None: 
                well_clip = prop_clip
            else:
                well_clip = self._get_clip_values(combined_log, show_wells_type['clip'])
            for well_name, well in self.cube.data['wells'].items():
                well_il, well_xl = well['coord']
                if section_type == 'inline': 
                    if well_il == section_idx:
                        ax.imshow(well['log'], aspect='auto', cmap=self.config.get_cmap(well_cmap), 
                                  vmin=well_clip[0], vmax=well_clip[1],
                                  extent=(well_xl - well_width//2, well_xl + well_width//2, self.size[4], self.size[5]), 
                                  zorder=20)
                else:
                    if well_xl == section_idx:
                        ax.imshow(well['log'], aspect='auto', cmap=self.config.get_cmap(well_cmap), 
                                  vmin=well_clip[0], vmax=well_clip[1],
                                  extent=(well_il - well_width//2, well_il + well_width//2, self.size[4], self.size[5]), 
                                  zorder=20)
        
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        
        # Labels & title
        ax.set_xlabel(x_label, **self.config.label_style)
        ax.set_ylabel(t_axis_label, **self.config.label_style)
        ax.set_title(title, **self.config.title_style)
        
  
        if show_seismic_type is not None and show_seismic_type['bar']:
            cbar = fig.colorbar(c1, ax=ax, aspect=30, shrink=1.0, pad=0.01)
            # cbar.set_label(unit_label, **self.config.label_style, labelpad=2)
        elif show_properties_type is not None and show_properties_type['bar']:
            cbar = fig.colorbar(c2, ax=ax, aspect=30, shrink=1.0, pad=0.01)
            if unit_label_p is not None:
                cbar.set_label(unit_label_p, **self.config.label_style, labelpad=2)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        
        plt.show()
        
        
    def plot_2d_section(self,
        data_2d: np.ndarray,
        extent=None,
        horizons=None,
        clip: Optional[Union[Tuple[float, float], str]] = None,
        t_axis_label="Time (ms)",
        x_label="Trace",
        figsize: Tuple[int, int] = (10, 4),
        cmap='Grey_scales',
        wells: Union[np.ndarray, List[np.ndarray]] = None,
        wells_pos: Union[int, List[int]] = None,
        well_cmap='AI',
        well_width: int = 4,
        unit_label = None, # 'g/cm³·m/s'
        save_path=None,
        show_colorbar=True,
        **kwargs
    ):
        "this fuction need 2d data"
        # Setup figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Clipping
        vmin, vmax = self._get_clip_values(data_2d, clip)
        
        if extent is None:
            extent = [0, data_2d.shape[1], 0, data_2d.shape[0]]
        
        # Main section plot
        c = ax.imshow(
            data_2d, aspect='auto', cmap=self.config.get_cmap(cmap),
            vmin=vmin, vmax=vmax,
            extent=extent, origin='upper', **kwargs
        )
        
        # Wells overlay
        if wells is not None:
            if isinstance(wells, list):
                 for i, well in enumerate(wells):
                     pos = wells_pos[i]
                     ax.imshow(well, aspect='auto', cmap=self.config.get_cmap(well_cmap), vmin=vmin, vmax=vmax,
                               extent=(pos - well_width//2, pos + well_width//2, extent[-2], extent[-1]), zorder=20 + i)
            else:
                ax.imshow(wells, aspect='auto', cmap=self.config.get_cmap(well_cmap), vmin=vmin, vmax=vmax,
                          extent=(wells_pos - well_width//2, wells_pos + well_width//2, extent[-2], extent[-1]), zorder=20)
        
        # Colorbar
        if show_colorbar:
            cbar = fig.colorbar(c, ax=ax, aspect=30, shrink=1.0, pad=0.01)
            # cbar.ax.text(0.5, 1.02, 'g/cm³·m/s', ha='center', va='bottom', fontsize=self.config.label_fontsize, transform=cbar.ax.transAxes)
            # cbar.set_label('(g/cm³)', **self.config.label_style, labelpad=2)
            if unit_label is not None:
                cbar.set_label(unit_label, **self.config.label_style, labelpad=2)
        
        # Horizons
        if horizons is not None:
            color_iter = itertools.cycle(['lime', 'magenta', 'blue', 'cyan', 'orange', 'yellow', 'red'])
            for name, df in horizons.items():
                if not df.empty:
                    x_vals = df.X if 'X' in df.columns else df.index
                    z_vals = df.Z if 'Z' in df.columns else df.values
                    ax.plot(x_vals, z_vals, lw=2.5, label=name, color=next(color_iter))
            ax.legend(loc='upper right')
        
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        
        # Labels & title
        ax.set_xlabel(x_label, **self.config.label_style)
        ax.set_ylabel(t_axis_label, **self.config.label_style)
        # ax.set_title(title, **self.config.title_style)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        
        plt.show()

