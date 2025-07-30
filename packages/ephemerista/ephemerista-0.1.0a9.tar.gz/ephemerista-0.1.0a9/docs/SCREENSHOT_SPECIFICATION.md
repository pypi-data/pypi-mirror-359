# Screenshot Specification for Ephemerista Documentation

This document specifies the exact screenshots needed to replace the 33 placeholder images in the documentation.

## Image Requirements

- **Format**: PNG (preferred for sharp UI elements)
- **Resolution**: High DPI/Retina quality (minimum 1440px wide for main interfaces)
- **Browser**: Use Chrome or Firefox for consistency
- **Zoom Level**: 100% browser zoom
- **Window Size**: Standard desktop size (1920x1080 or similar)

## Screenshot Categories

### 1. Interface Overview (4 screenshots)

#### 1.1 Main Application Interface
- **File**: `docs/images/gui/main-interface.png`
- **Placeholder Location**: Line 82
- **Description**: "Main application interface showing the three-panel layout with scenario configuration on the left, 3D visualization in the center, and analysis panel on the right"
- **Content to Show**:
  - Full browser window with Ephemerista loaded
  - Left panel: Scenario configuration forms
  - Center panel: 3D Earth visualization
  - Right panel: Analysis controls
  - Clear separation between panels

#### 1.2 Interface Overview with Labels
- **File**: `docs/images/gui/interface-overview-labeled.png`
- **Placeholder Location**: Line 134
- **Description**: "Interface overview with labeled panels"
- **Content to Show**:
  - Same as 1.1 but with overlay labels pointing to:
    - "Scenario Configuration"
    - "3D Visualization"
    - "Analysis Panel"
    - Key buttons and controls

#### 1.3 Time Control Interface
- **File**: `docs/images/gui/time-controls.png`
- **Placeholder Location**: Line 1368
- **Description**: "Time control interface at bottom of 3D viewer"
- **Content to Show**:
  - Close-up of time control bar
  - Play/pause buttons
  - Time slider
  - Speed controls
  - Current time display

#### 1.4 3D Viewer with Controls
- **File**: `docs/images/gui/3d-viewer-controls.png`
- **Placeholder Location**: Line 507
- **Description**: "3D viewer with visible camera control indicators"
- **Content to Show**:
  - 3D Earth view
  - Camera control icons/indicators
  - Zoom controls
  - Reset view button

### 2. Scenario Configuration (6 screenshots)

#### 2.1 Scenario Configuration Form
- **File**: `docs/images/gui/scenario-configuration.png`
- **Placeholder Location**: Line 233
- **Description**: "Scenario configuration form showing time settings, reference frame selection, and origin selection"
- **Content to Show**:
  - Scenario name field
  - Start/end time pickers
  - Time step input
  - Reference frame dropdown
  - Origin selection

#### 2.2 Time Scale Selection
- **File**: `docs/images/gui/time-scale-dropdown.png`
- **Placeholder Location**: Line 272
- **Description**: "Time scale selection dropdown with available options"
- **Content to Show**:
  - Dropdown menu open showing:
    - UTC
    - TAI
    - TT
    - GPS

#### 2.3 Asset Type Selection
- **File**: `docs/images/gui/asset-type-dialog.png`
- **Placeholder Location**: Line 339
- **Description**: "Asset type selection dialog"
- **Content to Show**:
  - Modal dialog with options:
    - Spacecraft
    - Ground Station
  - Add Asset button highlighted

#### 2.4 Spacecraft Configuration Form
- **File**: `docs/images/gui/spacecraft-configuration.png`
- **Placeholder Location**: Line 368
- **Description**: "Spacecraft configuration form with propagator selection"
- **Content to Show**:
  - Spacecraft name field
  - Propagator type dropdown (SGP4, Numerical, etc.)
  - Initial configuration fields

#### 2.5 Ground Station Configuration
- **File**: `docs/images/gui/ground-station-configuration.png`
- **Placeholder Location**: Line 460
- **Description**: "Ground station configuration form with geographic coordinates"
- **Content to Show**:
  - Ground station name
  - Longitude/latitude inputs
  - Altitude field
  - Minimum elevation setting

#### 2.6 Area of Interest Definition
- **File**: `docs/images/gui/area-of-interest-definition.png`
- **Placeholder Location**: Line 1145
- **Description**: "Area of interest definition interface with map view"
- **Content to Show**:
  - Map interface for drawing areas
  - Tools for shape creation
  - GeoJSON import option

### 3. Orbit Setup (4 screenshots)

#### 3.1 LEO Quick Setup
- **File**: `docs/images/gui/leo-quick-setup.png`
- **Placeholder Location**: Line 509
- **Description**: "LEO quick setup form"
- **Content to Show**:
  - LEO-specific configuration options
  - Altitude range settings
  - Inclination input

#### 3.2 MEO Quick Setup
- **File**: `docs/images/gui/meo-quick-setup.png`
- **Placeholder Location**: Line 516
- **Description**: "MEO quick setup form"
- **Content to Show**:
  - MEO configuration options
  - Semi-synchronous settings

#### 3.3 GEO Quick Setup
- **File**: `docs/images/gui/geo-quick-setup.png`
- **Placeholder Location**: Line 523
- **Description**: "GEO quick setup form"
- **Content to Show**:
  - GEO configuration with fixed altitude
  - Longitude positioning

#### 3.4 SSO Quick Setup
- **File**: `docs/images/gui/sso-quick-setup.png`
- **Placeholder Location**: Line 530
- **Description**: "SSO quick setup form"
- **Content to Show**:
  - Sun-synchronous orbit options
  - LTAN (Local Time of Ascending Node) settings

### 4. Propagation Configuration (3 screenshots)

#### 4.1 SGP4 Configuration
- **File**: `docs/images/gui/sgp4-configuration.png`
- **Placeholder Location**: Line 537
- **Description**: "SGP4 configuration form with TLE input field"
- **Content to Show**:
  - TLE input text area
  - Two-line element format example
  - Validation indicators

#### 4.2 Numerical Propagator Configuration
- **File**: `docs/images/gui/numerical-propagator-config.png`
- **Placeholder Location**: Line 544
- **Description**: "Numerical propagator configuration with force model options"
- **Content to Show**:
  - Force model checkboxes
  - Gravity degree/order settings
  - Atmospheric drag options
  - Solar radiation pressure settings

#### 4.3 OEM File Upload
- **File**: `docs/images/gui/oem-file-upload.png`
- **Placeholder Location**: Line 550
- **Description**: "OEM file upload interface"
- **Content to Show**:
  - File upload dialog
  - OEM format validation
  - Interpolation settings

### 5. Analysis Results (8 screenshots)

#### 5.1 Analysis Panel Selection
- **File**: `docs/images/gui/analysis-panel-visibility.png`
- **Placeholder Location**: Line 574
- **Description**: "Analysis panel with visibility option selected"
- **Content to Show**:
  - Analysis dropdown menu
  - Visibility analysis selected
  - Run Analysis button

#### 5.2 Visibility Results Table
- **File**: `docs/images/gui/visibility-results-table.png`
- **Placeholder Location**: Line 581
- **Description**: "Visibility results table showing pass data"
- **Content to Show**:
  - Table with columns:
    - Start Time
    - End Time
    - Duration
    - Max Elevation
  - Multiple pass entries

#### 5.3 Pass Details Plot
- **File**: `docs/images/gui/pass-elevation-plot.png`
- **Placeholder Location**: Line 589
- **Description**: "Detailed pass plot showing elevation and azimuth over time"
- **Content to Show**:
  - Time-series plot
  - Elevation curve
  - Azimuth data
  - Range information

#### 5.4 Link Budget Configuration
- **File**: `docs/images/gui/link-budget-configuration.png`
- **Placeholder Location**: Line 921
- **Description**: "Link budget analysis configuration options"
- **Content to Show**:
  - Analysis options checkboxes
  - Include Interference toggle
  - Environmental losses settings

#### 5.5 Link Budget Results
- **File**: `docs/images/gui/link-budget-results.png`
- **Placeholder Location**: Line 964
- **Description**: "Link budget results table showing all performance metrics"
- **Content to Show**:
  - Results table with:
    - EIRP values
    - Path Loss
    - C/N0 ratios
    - Link Margins

#### 5.6 Coverage Analysis Configuration
- **File**: `docs/images/gui/coverage-analysis-config.png`
- **Placeholder Location**: Line 1176
- **Description**: "Coverage analysis configuration panel"
- **Content to Show**:
  - Temporal resolution settings
  - Minimum elevation input
  - Coverage criteria options

#### 5.7 Coverage Metrics Summary
- **File**: `docs/images/gui/coverage-metrics-summary.png`
- **Placeholder Location**: Line 1213
- **Description**: "Coverage metrics summary table"
- **Content to Show**:
  - Coverage percentage
  - Maximum gap duration
  - Revisit time statistics
  - Mean access duration

#### 5.8 Navigation Analysis Setup
- **File**: `docs/images/gui/navigation-analysis-setup.png`
- **Placeholder Location**: Line 1250
- **Description**: "Navigation analysis setup with GNSS constellation"
- **Content to Show**:
  - GNSS constellation configuration
  - Observer setup
  - DOP requirements

### 6. Communication Systems (4 screenshots)

#### 6.1 Communication System Configuration
- **File**: `docs/images/gui/comms-system-config.png`
- **Placeholder Location**: Line 764
- **Description**: "Communication system configuration section"
- **Content to Show**:
  - Add Communication System button
  - System components list
  - Configuration forms

#### 6.2 Simple Antenna Configuration
- **File**: `docs/images/gui/simple-antenna-config.png`
- **Placeholder Location**: Line 772
- **Description**: "Simple antenna configuration form"
- **Content to Show**:
  - Antenna gain input
  - Beamwidth setting
  - Boresight vector fields

#### 6.3 Transmitter Configuration
- **File**: `docs/images/gui/transmitter-config.png`
- **Placeholder Location**: Line 824
- **Description**: "Transmitter configuration form"
- **Content to Show**:
  - Power setting
  - Frequency input
  - Line loss configuration
  - Modulation options

#### 6.4 Channel Configuration
- **File**: `docs/images/gui/channel-config.png`
- **Placeholder Location**: Line 851
- **Description**: "Channel configuration form with all parameters"
- **Content to Show**:
  - Channel name
  - Link type selection
  - Data rate input
  - Required Eb/N0
  - Link margin settings

### 7. Constellation Design (2 screenshots)

#### 7.1 Walker Constellation Configuration
- **File**: `docs/images/gui/walker-constellation-config.png`
- **Placeholder Location**: Line 1020
- **Description**: "Walker Star constellation configuration form"
- **Content to Show**:
  - Number of satellites
  - Number of planes
  - Phasing parameters
  - Orbital parameters

#### 7.2 Streets-of-Coverage Configuration
- **File**: `docs/images/gui/streets-coverage-config.png`
- **Placeholder Location**: Line 1049
- **Description**: "Streets-of-Coverage configuration form"
- **Content to Show**:
  - Coverage latitude bounds
  - Longitude spacing
  - Sun-synchronous settings

### 8. Visualization and Results (8 screenshots)

#### 8.1 3D Visualization with Elements
- **File**: `docs/images/gui/3d-visualization-elements.png`
- **Placeholder Location**: Line 1353
- **Description**: "3D visualization with all display elements enabled"
- **Content to Show**:
  - Earth model
  - Satellite models
  - Orbital paths
  - Ground station markers
  - Visibility cones

#### 8.2 Ground Tracks and Visibility
- **File**: `docs/images/gui/ground-tracks-visibility.png`
- **Placeholder Location**: Line 597
- **Description**: "3D visualization showing satellite ground tracks and visibility cones"
- **Content to Show**:
  - Satellite ground track projections
  - Visibility coverage areas
  - Real-time position updates

#### 8.3 Walker Constellation View
- **File**: `docs/images/gui/walker-constellation-3d.png`
- **Placeholder Location**: Line 1124
- **Description**: "3D visualization of a Walker constellation showing multiple orbital planes"
- **Content to Show**:
  - Multiple orbital planes
  - Distributed satellites
  - Constellation geometry

#### 8.4 Coverage Map
- **File**: `docs/images/gui/coverage-map.png`
- **Placeholder Location**: Line 1234
- **Description**: "Coverage map showing colored regions indicating coverage levels"
- **Content to Show**:
  - World map with coverage overlay
  - Color-coded coverage regions
  - Coverage percentage indicators

#### 8.5 Layer Control Panel
- **File**: `docs/images/gui/layer-control-panel.png`
- **Placeholder Location**: Line 1385
- **Description**: "Layer control panel with checkboxes for different visualization elements"
- **Content to Show**:
  - Checkboxes for:
    - Satellites
    - Trajectories
    - Ground tracks
    - Coverage zones
    - Communication links

#### 8.6 Export Dialog
- **File**: `docs/images/gui/export-dialog.png`
- **Placeholder Location**: Line 1398
- **Description**: "Export dialog with format options"
- **Content to Show**:
  - Export format dropdown
  - JSON, CSV, CCSDS options
  - Export button

#### 8.7 TLE Import Interface
- **File**: `docs/images/gui/tle-import-interface.png`
- **Placeholder Location**: Line 1407
- **Description**: "TLE import interface with text area for pasting TLE data"
- **Content to Show**:
  - TLE text input area
  - Import TLE button
  - Format validation

#### 8.8 Help Menu
- **File**: `docs/images/gui/help-menu.png`
- **Placeholder Location**: Line 1429
- **Description**: "Help menu with links to documentation and support resources"
- **Content to Show**:
  - Help dropdown menu
  - Documentation links
  - Support resources

## Screenshot Scenarios to Prepare

1. **Empty Scenario**: Start with a clean slate
2. **Basic LEO Scenario**: Single satellite in LEO orbit
3. **Ground Station Scenario**: Add ground stations for visibility analysis
4. **Constellation Scenario**: Walker constellation example
5. **Analysis Results**: Run analyses to show results

## Delivery Instructions

1. Save all images in PNG format
2. Use descriptive filenames matching the specification
3. Ensure images are high quality and readable
4. Include any scenario files used to generate the screenshots
5. Test that all GUI elements are clearly visible

## Notes for Screenshot Capture

- Use consistent browser/OS combination
- Ensure UI text is readable at documentation display sizes
- Capture full dialogs/forms when showing configuration
- Include relevant context (don't crop too tightly)
- Show realistic data/examples rather than empty forms where possible