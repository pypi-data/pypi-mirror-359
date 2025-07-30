# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Climate Zarr Toolkit - An interactive CLI for processing climate data with NetCDF to Zarr conversion and county-level statistical analysis. Built with modern Python tools emphasizing user experience through interactive prompts and wizards.

## Development Commands

### Installation and Setup
```bash
# Install dependencies in development mode (always use uv)
uv install
# or
uv pip install -e .

# Run Python commands
uv run python <script.py>
```

### Running the CLI
```bash
# Main CLI (after installation)
climate-zarr

# Direct execution
python climate_cli.py

# Interactive wizard mode (recommended for new users)
python climate_cli.py wizard

# Individual commands with interactive prompts
python climate_cli.py create-zarr
python climate_cli.py county-stats
python climate_cli.py info

# Demo script
python demo_cli.py
```

### Data Preparation
```bash
# Split county shapefiles by region (required before county stats)
cd utils
uv run python split_counties_by_region.py
```

## Architecture

### Core Components
1. **climate_cli.py** - Main Typer CLI application with commands:
   - `create-zarr`: Convert NetCDF files to Zarr format
   - `county-stats`: Calculate climate statistics by county
   - `wizard`: Interactive guided workflow
   - `info`: Check data availability
   - `list-regions`: Show available regions

2. **stack_nc_to_zarr.py** - NetCDF to Zarr conversion engine:
   - Handles multiple compression algorithms (zstd, lz4, gzip, blosc)
   - Regional clipping with shapefile boundaries
   - Parallel processing with Dask
   - Smart chunking strategies

3. **calculate_county_stats.py** - County statistics processor:
   - Calculates mean, sum, min, max, percentiles
   - Supports precipitation and temperature variables
   - Parallel processing with multiprocessing or Dask
   - Outputs detailed CSV with metadata

4. **climate_config.py** - Pydantic 2 configuration management:
   - Hierarchical config: environment vars → file → CLI args → prompts
   - Pre-defined regions (CONUS, Alaska, Hawaii, Guam, Puerto Rico)
   - Compression and chunking settings
   - Processing options

### Data Flow
```
NetCDF Files → Zarr Store (with compression/clipping) → County Statistics → CSV Output
              ↓                                        ↓
        Configuration                           Regional Shapefiles
```

### Interactive UX Pattern
All commands default to interactive mode with:
- Questionary prompts for user inputs
- Rich progress bars and status updates
- Confirmation dialogs for destructive operations
- Smart defaults and suggestions
- Beautiful formatted output with panels and tables

## Development Guidelines

### Key Dependencies
- **CLI**: Typer with Rich integration
- **Interactive**: Questionary for prompts
- **Data**: xarray, zarr, dask, pandas, geopandas
- **Geospatial**: rioxarray, shapely, pyogrio
- **Cloud**: virtualizarr, kerchunk, s3fs, fsspec
- **Validation**: Pydantic 2

### Code Patterns
1. Always use Rich for terminal output (progress bars, panels, tables)
2. Use Pydantic 2 models for configuration and validation
3. Implement both interactive and non-interactive modes
4. Use descriptive variable names throughout
5. Handle errors gracefully with helpful messages
6. Support parallel processing where applicable

### Testing Approach
- Use real API calls for tests (no mocking)
- Test with actual climate data files
- Verify output formats and data integrity
- Test both interactive and CLI modes

### Performance Considerations
- Default to Dask for large datasets
- Use appropriate chunk sizes (512x512 default)
- Enable compression (zstd default)
- Support distributed processing
- Memory-efficient streaming operations

## Common Tasks

### Adding New Climate Variables
1. Update `ClimateVariable` enum in climate_config.py
2. Add variable metadata (units, description)
3. Update processing logic if needed
4. Test with sample data

### Adding New Regions
1. Add region definition to `REGIONS` in climate_config.py
2. Ensure corresponding shapefile exists in regional_counties/
3. Update documentation

### Modifying Compression Settings
1. Update `CompressionSettings` in climate_config.py
2. Test performance with different algorithms
3. Consider memory vs. speed tradeoffs

## Important Notes

- Users must provide their own NetCDF climate data files
- County shapefiles must be downloaded from US Census and prepared using utils scripts
- The project supports cloud-native workflows with S3 and reference file systems
- Interactive mode is the default - use `--no-interactive` for automation
- All file paths should be validated before processing
- Memory usage scales with chunk size and compression settings