# Ephemerista User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [Getting Started](#getting-started)
4. [Scenario Configuration](#scenario-configuration)
5. [Spacecraft and Ground Station Configuration](#spacecraft-and-ground-station-configuration)
6. [Propagation Setup](#propagation-setup)
7. [Visibility Analysis](#visibility-analysis)
8. [Communication Systems Configuration](#communication-systems-configuration)
9. [Link Budget Analysis](#link-budget-analysis)
10. [Constellation Configuration](#constellation-configuration)
11. [Coverage Analysis](#coverage-analysis)
12. [Navigation Analysis](#navigation-analysis)
13. [Visualization and Data Export](#visualization-and-data-export)
14. [Advanced Features](#advanced-features)
15. [Examples and Tutorials](#examples-and-tutorials)
16. [Troubleshooting and Reference](#troubleshooting-and-reference)

## Introduction

Ephemerista is a comprehensive space mission analysis tool that provides capabilities for satellite constellation design, orbital propagation, visibility analysis, communication link budgets, coverage analysis, and navigation performance evaluation. It offers both a web-based graphical user interface (GUI) and a Python API for programmatic access.

### Key Features
- Interactive 3D visualization of satellites and ground stations
- Multiple orbital propagation methods (SGP4, numerical, semi-analytical, OEM)
- Visibility and coverage analysis for satellite constellations
- RF link budget calculations with interference modeling
- Navigation dilution of precision (DOP) analysis
- Constellation design tools (Walker patterns, Streets-of-Coverage)
- Communication system modeling with antenna patterns
- Extensible framework for custom analysis workflows

### Architecture Overview

Ephemerista is built on several core concepts:

- **Scenarios**: Central container for mission configurations (see {doc}`../api/scenarios`)
- **Assets**: Spacecraft and ground stations with associated properties (see {doc}`../api/assets`)
- **Propagators**: Orbital mechanics engines (SGP4, numerical, semi-analytical) (see {doc}`../api/propagators/index`)
- **Ensembles**: Collections of propagated trajectories (see {doc}`../api/scenarios`)
- **Analysis Modules**: Specialized calculators for different mission aspects (see {doc}`../api/analysis/index`)

### GUI vs Python API

**Use the GUI when:**
- Performing interactive mission design
- Visualizing orbital scenarios in 3D
- Quick prototyping and what-if analyses
- Demonstrating concepts to stakeholders

**Use the Python API when:**
- Automating complex analysis workflows
- Performing batch processing or optimization
- Integrating with other tools
- Developing custom analysis modules

For complete API documentation, see the {doc}`../api/index`.

## Installation and Setup

### System Requirements

#### GUI Requirements
- Modern web browser with WebGL support
- Internet connection for initial loading
- Recommended: Chrome, Firefox, or Safari

#### Python API Requirements
- Python 3.12 or higher
- Required data files: Earth Orientation Parameters (EOP), planetary ephemerides, and Orekit data package

### Installation

#### GUI Access

1. Navigate to the Ephemerista web interface
2. The application loads with a default empty scenario

```{figure} ../images/gui/main-interface.png
:name: main-interface
:alt: Main application interface
:class: screenshot

Main application interface showing the three-panel layout with scenario configuration on the left, 3D visualization in the center, and analysis panel on the right
```

#### Python API Installation

```bash
pip install ephemerista
```

### Data File Setup

Both GUI and Python require data files for high-precision calculations:

#### Earth Orientation Parameters (EOP)
- **File**: `finals2000A.all.csv` from IERS
- **Purpose**: High-precision coordinate transformations
- **Update Frequency**: Weekly recommended

#### Planetary Ephemerides
- **File**: DE440s or similar JPL ephemeris file
- **Purpose**: Precise planetary positions for perturbation calculations
- **Format**: SPICE kernel (.bsp)

### Initialization

#### GUI Initialization
The GUI automatically loads required data files when starting.

#### Python Initialization

```python
import ephemerista

# Initialize with data directory containing EOP and ephemeris files
ephemerista.init(
    eop_file="path/to/finals2000A.all.csv",
    ephemeris_file="path/to/de440s.bsp",
    orekit_data_dir="path/to/orekit-data"  # Optional
)
```

*[CODE BLOCK PLACEHOLDER: Complete initialization example with error handling]*

## Getting Started

### GUI: Launching the Application

The Ephemerista GUI consists of three main sections:

- **Left Panel**: Scenario configuration forms
- **Center Panel**: 3D visualization and analysis results (tabbed interface)
- **Right Panel**: Analysis controls and results

```{figure} ../images/gui/interface-overview-labeled.png
:name: interface-overview
:alt: Interface overview with labeled panels
:class: screenshot

Interface overview with labeled panels showing the main components of the Ephemerista GUI
```

### Python: Basic Script Structure

```python
#!/usr/bin/env python3
import ephemerista
from ephemerista import Scenario
from ephemerista.time import Epoch, TimeScale
from datetime import datetime, timezone

# Initialize Ephemerista
ephemerista.init(
    eop_file="data/finals2000A.all.csv",
    ephemeris_file="data/de440s.bsp"
)

# Create a scenario
scenario = Scenario(
    name="My First Mission",
    start_time=Epoch.from_datetime(
        datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        TimeScale.UTC
    ),
    end_time=Epoch.from_datetime(
        datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
        TimeScale.UTC
    ),
    time_step=60.0  # seconds
)
```

### Quick Example: Simple Scenario

#### GUI Approach

1. Enter scenario name: "LEO Observation Mission"
2. Set start and end times using the date/time pickers (see [Scenario Configuration](#scenario-configuration))
3. Click "Add Asset" → "Spacecraft"
4. Select "SGP4" propagator and paste a TLE (see [Spacecraft Configuration](#spacecraft-and-ground-station-configuration))
5. Click "Add Asset" → "Ground Station"
6. Enter location coordinates (see [Ground Station Configuration](#spacecraft-and-ground-station-configuration))
7. Navigate to "Analyses" tab and select "Visibility" (see [Visibility Analysis](#visibility-analysis))
8. Click "Run Analysis"

#### Python Approach

```python
from ephemerista.assets import Spacecraft, GroundStation
from ephemerista.propagators.sgp4 import Sgp4Propagator

# Create spacecraft from TLE
tle_line1 = "1 25544U 98067A   21001.00000000  .00000000  00000-0  00000+0 0    06"
tle_line2 = "2 25544  51.6400 000.0000 0000000   0.0000 000.0000 15.50000000000000"

spacecraft = Spacecraft(
    name="ISS",
    propagator=Sgp4Propagator.from_tle(tle_line1, tle_line2)
)

# Create ground station
ground_station = GroundStation(
    name="Mission Control",
    longitude=-95.4,
    latitude=29.6,
    altitude=50.0,
    minimum_elevation=10.0
)

# Add to scenario
scenario.add_asset(spacecraft)
scenario.add_asset(ground_station)

# Run visibility analysis
from ephemerista.analysis.visibility import Visibility
visibility_analyzer = Visibility(scenario)
results = visibility_analyzer.calculate()
```

## Scenario Configuration

### Basic Scenario Setup

Scenarios are the central containers for mission analysis. They define the temporal boundaries and coordinate systems for all calculations.

```{seealso}
For detailed API documentation, see {doc}`../api/scenarios` and {doc}`../api/time`.
```

#### GUI Configuration

1. **Scenario Name**: Enter a descriptive name for your scenario
2. **Time Configuration**:
   - **Start Time**: Set the simulation start time (UTC)
   - **End Time**: Set the simulation end time (UTC)
   - **Time Step**: Define the temporal resolution in seconds
3. **Reference Frame**: Select the coordinate reference frame (typically ICRF)
4. **Origin**: Choose the central body (typically Earth)

```{figure} ../images/gui/scenario-configuration.png
:name: scenario-config
:alt: Scenario configuration form
:class: screenshot

Scenario configuration form showing time settings, reference frame selection, and origin selection
```

#### Python Configuration

```python
from ephemerista import Scenario
from ephemerista.time import Epoch, TimeScale
from ephemerista.frames import ReferenceFrame
from datetime import datetime, timezone

# Create a new scenario
scenario = Scenario(
    name="Mission Analysis Example",
    start_time=Epoch.from_datetime(
        datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        TimeScale.UTC
    ),
    end_time=Epoch.from_datetime(
        datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
        TimeScale.UTC
    ),
    time_step=60.0  # seconds
)

# Configure reference frame (optional, defaults to ICRF)
scenario.reference_frame = ReferenceFrame.ICRF
```

### Time Scale Management

Ephemerista supports multiple time scales:

- **UTC**: Coordinated Universal Time
- **TAI**: International Atomic Time
- **TT**: Terrestrial Time
- **GPS**: GPS Time

#### GUI Time Scale Selection

```{figure} ../images/gui/time-scale-dropdown.png
:name: time-scale-dropdown
:alt: Time scale selection dropdown
:class: screenshot

Time scale selection dropdown with available options (UTC, TAI, TT, GPS)
```

#### Python Time Scale Usage

```python
from ephemerista.time import TimeScale

# Available time scales
time_scales = [
    TimeScale.UTC,    # Coordinated Universal Time
    TimeScale.TAI,    # International Atomic Time
    TimeScale.TT,     # Terrestrial Time
    TimeScale.GPS     # GPS Time
]

# Convert between time scales
utc_epoch = Epoch.from_datetime(datetime.now(timezone.utc), TimeScale.UTC)
tai_epoch = utc_epoch.to_time_scale(TimeScale.TAI)
```

### Reference Frames

Configure coordinate reference frames:

```{seealso}
For complete reference frame documentation, see {doc}`../api/frames`.
```

#### Common Reference Frames
- **ICRF**: International Celestial Reference Frame
- **GCRF**: Geocentric Celestial Reference Frame
- **ITRF**: International Terrestrial Reference Frame
- **EME2000**: Earth Mean Equator 2000

#### Python Reference Frame Configuration

```python
from ephemerista.frames import ReferenceFrame

# Common reference frames
frames = {
    "ICRF": ReferenceFrame.ICRF,      # International Celestial Reference Frame
    "GCRF": ReferenceFrame.GCRF,      # Geocentric Celestial Reference Frame
    "ITRF": ReferenceFrame.ITRF,      # International Terrestrial Reference Frame
    "EME2000": ReferenceFrame.EME2000  # Earth Mean Equator 2000
}

scenario.reference_frame = ReferenceFrame.ICRF
```

## Spacecraft and Ground Station Configuration

### Adding Assets

Assets are the physical entities in your scenario - spacecraft orbiting in space and ground stations on Earth.

```{seealso}
For complete asset API documentation, see {doc}`../api/assets`.
```

#### GUI: Adding Assets

1. Click the **"Add Asset"** button in the scenario configuration panel
2. Choose between:
   - **Spacecraft**: Orbiting vehicles
   - **Ground Station**: Earth-based facilities

*[SCREENSHOT PLACEHOLDER: Asset type selection dialog]*

#### Python: Creating Assets

```python
from ephemerista.assets import Spacecraft, GroundStation
```

### Spacecraft Configuration

#### Propagator Types

Ephemerista supports multiple propagation methods:

1. **SGP4**: For TLE-based propagation
2. **Numerical**: High-precision numerical integration
3. **Semi-Analytical**: Analytical mean element propagation
4. **OEM**: Orbit Ephemeris Message input

```{seealso}
For detailed propagator documentation, see {doc}`../api/propagators/index`.
```

#### GUI: Spacecraft Setup

1. **Name**: Enter a unique identifier for the spacecraft
2. **Propagator Type**: Select from dropdown menu
3. Configure propagator-specific parameters

*[SCREENSHOT PLACEHOLDER: Spacecraft configuration form with propagator selection]*

#### Python: Spacecraft Creation

##### Using SGP4 with TLE

```python
from ephemerista.propagators.sgp4 import Sgp4Propagator

# Create spacecraft from TLE
tle_line1 = "1 25544U 98067A   21001.00000000  .00000000  00000-0  00000+0 0    06"
tle_line2 = "2 25544  51.6400 000.0000 0000000   0.0000 000.0000 15.50000000000000"

spacecraft_tle = Spacecraft(
    name="ISS",
    propagator=Sgp4Propagator.from_tle(tle_line1, tle_line2)
)

scenario.add_asset(spacecraft_tle)
```

##### Using Keplerian Elements

```python
from ephemerista.coords.twobody import KeplerianElements
from ephemerista.propagators.sgp4 import Sgp4Propagator

# Define orbital elements
elements = KeplerianElements(
    semi_major_axis=7000.0,    # km
    eccentricity=0.001,
    inclination=98.0,          # degrees
    raan=0.0,                  # Right Ascension of Ascending Node
    argument_of_periapsis=0.0,
    true_anomaly=0.0
)

# Create spacecraft with SGP4 propagator
spacecraft = Spacecraft(
    name="Earth Observer 1",
    propagator=Sgp4Propagator.from_keplerian_elements(
        elements, 
        epoch=scenario.start_time
    )
)

scenario.add_asset(spacecraft)
```

##### High-Precision Numerical Propagation

```python
from ephemerista.propagators.orekit.numerical import NumericalPropagator
from ephemerista.coords.trajectories import CartesianState

# Define initial state
initial_state = CartesianState(
    position=[7000.0, 0.0, 0.0],     # km
    velocity=[0.0, 7.5, 0.0],        # km/s
    epoch=scenario.start_time,
    frame=ReferenceFrame.ICRF
)

# Configure numerical propagator with force models
numerical_prop = NumericalPropagator(
    initial_state=initial_state,
    gravity_degree=20,        # Gravity field degree
    gravity_order=20,         # Gravity field order
    include_drag=True,        # Atmospheric drag
    include_srp=True,         # Solar radiation pressure
    include_third_body=True   # Moon/Sun perturbations
)

spacecraft_numerical = Spacecraft(
    name="High Precision Satellite",
    propagator=numerical_prop
)
```

### Ground Station Configuration

Ground stations are fixed locations on Earth's surface used for communication with spacecraft.

#### GUI: Ground Station Setup

1. **Name**: Enter ground station identifier
2. **Location**:
   - **Longitude**: East longitude in degrees
   - **Latitude**: North latitude in degrees  
   - **Altitude**: Height above sea level (meters)
3. **Minimum Elevation**: Minimum satellite elevation angle for visibility (degrees)

*[SCREENSHOT PLACEHOLDER: Ground station configuration form with geographic coordinates]*

#### Python: Ground Station Creation

```python
# Create ground station
ground_station = GroundStation(
    name="Deep Space Network Station",
    longitude=243.11,          # degrees East
    latitude=35.42,           # degrees North
    altitude=1036.0,          # meters above sea level
    minimum_elevation=10.0    # degrees
)

scenario.add_asset(ground_station)
```

### Asset Properties and Metadata

Assets can have custom properties for advanced analysis:

```python
# Add custom properties to assets
spacecraft.properties = {
    "mass": 500.0,           # kg
    "cross_section": 2.5,    # m²
    "drag_coefficient": 2.2,
    "srp_coefficient": 1.8,
    "mission_type": "Earth Observation"
}

# Asset identification and grouping
spacecraft.tags = ["EO", "polar", "sun_synchronous"]
ground_station.tags = ["DSN", "primary", "X_band"]
```

## Propagation Setup

### Orbit Types and Quick Setup

#### GUI: Quick Orbit Setup

Ephemerista provides quick setup options for common orbital regimes:

##### Low Earth Orbit (LEO)
- Altitude range: 200-2000 km
- Quick setup with altitude and inclination
- Automatic calculation of orbital period

*[SCREENSHOT PLACEHOLDER: LEO quick setup form]*

##### Medium Earth Orbit (MEO)
- Altitude range: 2000-35786 km
- Common for navigation satellites
- Semi-synchronous options available

*[SCREENSHOT PLACEHOLDER: MEO quick setup form]*

##### Geostationary Earth Orbit (GEO)
- Fixed altitude at 35,786 km
- Zero inclination and eccentricity
- Automatic longitude positioning

*[SCREENSHOT PLACEHOLDER: GEO quick setup form]*

##### Sun-Synchronous Orbit (SSO)
- Maintains consistent solar illumination
- Automatic inclination calculation based on altitude
- Ideal for Earth observation missions

*[SCREENSHOT PLACEHOLDER: SSO quick setup form]*

#### Python: Orbit Type Configuration

```python
# LEO Example
leo_elements = KeplerianElements(
    semi_major_axis=6878.0,    # 500 km altitude
    eccentricity=0.0,
    inclination=97.4,          # Sun-synchronous at this altitude
    raan=0.0,
    argument_of_periapsis=0.0,
    true_anomaly=0.0
)

# GEO Example
geo_elements = KeplerianElements(
    semi_major_axis=42164.0,   # GEO radius
    eccentricity=0.0,
    inclination=0.0,
    raan=0.0,
    argument_of_periapsis=0.0,
    true_anomaly=0.0
)
```

### Propagator Selection Guide

#### SGP4 Propagator
**Best for:**
- TLE-based analysis
- Large constellation studies
- Rapid computation requirements

**Limitations:**
- Lower accuracy for long-term predictions
- Not suitable for high-precision maneuver planning

#### Numerical Propagator
**Best for:**
- High-precision mission analysis
- Maneuver planning
- Formation flying studies

**Configuration:**
```python
numerical_prop = NumericalPropagator(
    initial_state=initial_state,
    gravity_degree=50,
    gravity_order=50,
    atmospheric_model="NRLMSISE00",
    solar_activity="STRONG",
    integrator="DormandPrince853",
    min_step=1e-3,
    max_step=300.0
)
```

#### Semi-Analytical Propagator
**Best for:**
- Long-term evolution studies
- Constellation maintenance analysis
- Orbit lifetime predictions

```python
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator

semi_analytical_prop = SemiAnalyticalPropagator(
    initial_state=initial_state,
    propagation_type="DSST",    # Draper Semi-analytical Satellite Theory
    mean_elements=True,
    short_period_corrections=True
)
```

### OEM (Orbit Ephemeris Message) Support

For precise ephemeris data:

#### GUI: OEM Import

1. Select **OEM** propagator type
2. Upload or paste OEM file content
3. Validate ephemeris data format
4. Set interpolation parameters

*[SCREENSHOT PLACEHOLDER: OEM file upload interface]*

#### Python: OEM Usage

```python
from ephemerista.propagators.oem import OemPropagator

# Load OEM file
oem_prop = OemPropagator.from_file("spacecraft_ephemeris.oem")

# Create spacecraft from OEM
spacecraft_oem = Spacecraft(
    name="Precision Ephemeris Satellite",
    propagator=oem_prop
)
```

### Ensemble Propagation

For efficient analysis of multiple assets:

```python
# Propagate entire scenario
ensemble = scenario.propagate()

# Access individual trajectories
for asset_id, trajectory in ensemble.trajectories.items():
    asset_name = ensemble.get_asset_name(asset_id)
    times = trajectory.times
    positions = trajectory.positions
    velocities = trajectory.velocities
```

## Visibility Analysis

### Understanding Visibility

Visibility analysis determines when spacecraft are visible from ground stations, accounting for elevation constraints and Earth obstruction.

```{seealso}
For complete visibility analysis API documentation, see {doc}`../api/analysis/visibility`.
```

### GUI: Running Visibility Analysis

1. Navigate to the **"Analyses"** tab
2. Select **"Visibility"** from the analysis type dropdown
3. Click **"Run Analysis"**

*[SCREENSHOT PLACEHOLDER: Analysis panel with visibility option selected]*

#### Visibility Results Display

The GUI displays visibility results in multiple formats:

- **Pass Summary Table**: Shows all visibility windows
- **Pass Timeline**: Visual representation of passes
- **Detailed Pass Information**: Elevation, azimuth, and range data

*[SCREENSHOT PLACEHOLDER: Visibility results table showing pass data]*

### Python: Visibility Analysis

```python
from ephemerista.analysis.visibility import Visibility

# Create visibility analyzer
visibility_analyzer = Visibility(scenario)

# Compute visibility
visibility_results = visibility_analyzer.calculate()

# Access visibility windows
for observer_id, observer_results in visibility_results.items():
    for target_id, passes in observer_results.items():
        for pass_data in passes:
            print(f"Pass from {pass_data.start_time} to {pass_data.end_time}")
            print(f"Maximum elevation: {pass_data.max_elevation} degrees")
```

### Advanced Visibility Options

#### Custom Elevation Masks

```python
from ephemerista.analysis.visibility import ElevationMask

# Define complex elevation mask
elevation_mask = ElevationMask({
    0: 10.0,      # 10° minimum at azimuth 0°
    90: 15.0,     # 15° minimum at azimuth 90°
    180: 8.0,     # 8° minimum at azimuth 180°
    270: 12.0     # 12° minimum at azimuth 270°
})

# Apply mask to ground station
ground_station.elevation_mask = elevation_mask
```

#### Visibility Constraints

```python
# Configure constraints
visibility_analyzer = Visibility(
    scenario,
    min_elevation=5.0,           # degrees
    max_range=2000.0,           # km
    eclipse_constraint=True,     # Exclude eclipsed satellites
    sun_elevation_limit=-6.0    # Twilight constraint
)
```

### Visualization Options

#### GUI: 3D Visualization

- **Ground Track**: Satellite orbital path projected onto Earth surface
- **Visibility Cones**: Ground station coverage areas
- **Real-time Position**: Current satellite locations

*[SCREENSHOT PLACEHOLDER: 3D visualization showing satellite ground tracks and visibility cones]*

#### Python: Plotting Visibility

```python
from ephemerista.plot.visibility import plot_visibility_pass

# Plot individual pass details
pass_plot = plot_visibility_pass(
    pass_data=passes[0],
    show_elevation=True,
    show_azimuth=True,
    show_range=True
)
```

## Communication Systems Configuration

### Overview

Communication systems model the RF links between spacecraft and ground stations, including antennas, transmitters, receivers, and channels.

```{seealso}
For complete communication systems API documentation, see {doc}`../api/comms/index`.
```

### Antenna Configuration

#### GUI: Adding Antennas

1. In the asset configuration, expand the **"Communication Systems"** section
2. Click **"Add Communication System"**
3. Configure antenna parameters

*[SCREENSHOT PLACEHOLDER: Communication system configuration section]*

#### Python: Antenna Types

##### Simple Antenna

```python
from ephemerista.comms.antennas import SimpleAntenna

# Create simple antenna
antenna = SimpleAntenna(
    gain=20.0,              # Peak gain in dB
    beamwidth=10.0,        # Half-power beamwidth in degrees
    design_frequency=2.4e9,    # Hz
    boresight_vector=[0, 0, 1] # Antenna pointing direction
)
```

##### Complex Antenna Patterns

```python
from ephemerista.comms.antennas import (
    GaussianPattern, 
    ParabolicPattern,
    DipolePattern
)

# Gaussian pattern antenna
gaussian_antenna = GaussianPattern(
    peak_gain=25.0,
    half_power_beamwidth=3.0,
    design_frequency=8.4e9
)

# Parabolic reflector
parabolic_antenna = ParabolicPattern(
    diameter=2.4,              # meters
    efficiency=0.65,
    design_frequency=8.4e9,
    feed_blockage_ratio=0.1
)
```

### Transmitter and Receiver Configuration

#### GUI Configuration

- **Transmitter**:
  - Power (watts)
  - Frequency (Hz)
  - Line losses (dB)
  - Output back-off (dB)

- **Receiver**:
  - Frequency (Hz)
  - System noise temperature (Kelvin)
  - Implementation losses (dB)

*[SCREENSHOT PLACEHOLDER: Transmitter and receiver configuration forms]*

#### Python Configuration

```python
from ephemerista.comms.transmitter import Transmitter
from ephemerista.comms.receiver import Receiver

transmitter = Transmitter(
    power=10.0,          # Transmit power in watts
    frequency=8.4e9,        # Operating frequency in Hz
    line_loss=1.5,          # System losses in dB
    output_backoff=3.0,     # Power amplifier backoff in dB
    modulation="QPSK",         # Modulation scheme
    symbol_rate=1e6            # Symbols per second
)

receiver = Receiver(
    frequency=8.4e9,
    system_noise_temperature=150.0,  # System noise temperature in Kelvin
    implementation_loss=1.0,         # Implementation losses in dB
    adc_bits=12,                        # ADC resolution
    bandwidth=2e6                    # Receiver bandwidth in Hz
)
```

### Channel Configuration

Channels define the communication link characteristics:

#### GUI: Channel Setup

1. **Channel Name**: Descriptive identifier
2. **Link Type**: 
   - **Uplink**: Ground-to-satellite
   - **Downlink**: Satellite-to-ground
   - **Crosslink**: Satellite-to-satellite
3. **Data Rate**: Information rate in bits per second
4. **Required Eb/N0**: Energy per bit to noise ratio (dB)
5. **Link Margin**: Additional margin for link reliability (dB)

*[SCREENSHOT PLACEHOLDER: Channel configuration form with all parameters]*

#### Python: Channel Definition

```python
from ephemerista.comms.channels import Channel

# Define communication channel
uplink_channel = Channel(
    name="S-band Uplink",
    link_type="uplink",
    frequency=2.1e9,
    data_rate=1e6,           # bits per second
    required_eb_n0=9.6,       # Required Eb/N0 in dB
    link_margin=3.0,          # Design margin in dB
    modulation="QPSK",
    forward_error_correction=0.5, # Coding rate
    roll_off_factor=0.35
)
```

### Communication System Integration

```python
from ephemerista.comms.systems import CommunicationSystem

# Create integrated communication system
comm_system = CommunicationSystem(
    name="Primary Communication System",
    antenna=gaussian_antenna,
    transmitter=transmitter,
    receiver=receiver,
    channels=[uplink_channel]
)

# Add to spacecraft
spacecraft.add_communication_system(comm_system)
```

## Link Budget Analysis

### Overview

Link budget analysis calculates the performance of RF communication links, accounting for all gains and losses in the signal path.

```{seealso}
For complete link budget analysis API documentation, see {doc}`../api/analysis/link_budget`.
```

### GUI: Running Link Budget Analysis

1. Ensure communication systems are configured for all assets
2. Navigate to the **"Analyses"** tab
3. Select **"Link Budget"** from the analysis dropdown
4. Configure analysis options:
   - **Include Interference**: Enable interference calculations
   - **Include Environmental Losses**: Account for atmospheric effects
5. Click **"Run Analysis"**

*[SCREENSHOT PLACEHOLDER: Link budget analysis configuration options]*

### Python: Link Budget Calculation

```python
from ephemerista.analysis.link_budget import LinkBudget

# Create link budget analyzer
link_budget_analyzer = LinkBudget(scenario)

# Compute link budgets
link_budget_results = link_budget_analyzer.calculate()

# Access link performance metrics
for link_id, link_data in link_budget_results.items():
    transmitter_name = link_data.transmitter_name
    receiver_name = link_data.receiver_name
    
    print(f"Link: {transmitter_name} -> {receiver_name}")
    print(f"EIRP: {link_data.eirp} dBW")
    print(f"Free Space Path Loss: {link_data.fspl} dB")
    print(f"C/N0: {link_data.cn0} dB-Hz")
    print(f"Eb/N0: {link_data.eb_n0} dB")
    print(f"Link Margin: {link_data.link_margin} dB")
```

### Understanding Link Budget Results

#### Key Metrics

- **EIRP**: Equivalent Isotropically Radiated Power (dBW)
- **Free Space Path Loss**: Signal attenuation due to distance (dB)
- **G/T**: Receiver figure of merit (dB/K)
- **C/N0**: Carrier-to-noise density ratio (dB-Hz)
- **Eb/N0**: Energy per bit to noise density ratio (dB)
- **Link Margin**: Available margin above required threshold (dB)

*[SCREENSHOT PLACEHOLDER: Link budget results table showing all performance metrics]*

### Environmental Effects

#### Atmospheric Losses

```python
# Configure atmospheric model
link_budget_analyzer = LinkBudget(
    scenario,
    atmospheric_model="ITU-R_P.676",
    surface_pressure=1013.25,      # hPa
    surface_temperature=15.0,      # °C
    relative_humidity=50.0,        # %
)
```

#### Rain Attenuation

```python
# Configure rain model
link_budget_analyzer = LinkBudget(
    scenario,
    rain_model="ITU-R_P.618",
    rain_rate=25.0,          # mm/hr exceeded 0.01% of time
    rain_height=2.0,         # km
)
```

### Interference Analysis

When enabled, interference analysis provides:
- **Interference power**: Unwanted signal levels
- **C/I ratio**: Carrier-to-interference ratio
- **Overall degradation**: Combined effect on link performance

*[SCREENSHOT PLACEHOLDER: Interference analysis results with C/I ratios]*

## Constellation Configuration

### Constellation Design Patterns

Ephemerista supports several constellation architectures:

```{seealso}
For complete constellation design API documentation, see {doc}`../api/constellation/index`.
```

### Walker Constellations

#### GUI: Walker Configuration

1. Select **"Add Constellation"** in the scenario panel
2. Choose constellation type:
   - **Walker Star**: Symmetric distribution
   - **Walker Delta**: Phased distribution

*[SCREENSHOT PLACEHOLDER: Walker constellation configuration form]*

#### Python: Walker Star

```python
from ephemerista.constellation.design import WalkerStar

walker_star = WalkerStar(
    num_satellites=24,          # Total satellites
    num_planes=4,              # Number of orbital planes
    inclination=55.0,      # Orbital inclination in degrees
    altitude=20200,         # Orbital altitude in km
    phasing_parameter=1        # Inter-plane phasing
)

# Generate constellation
constellation_assets = walker_star.generate_assets(
    base_name="GPS",
    start_epoch=scenario.start_time
)

# Add to scenario
for asset in constellation_assets:
    scenario.add_asset(asset)
```

#### Python: Walker Delta

```python
from ephemerista.constellation.design import WalkerDelta

walker_delta = WalkerDelta(
    num_satellites=27,
    num_planes=3,
    inclination=86.4,
    altitude=1414,
    pattern_factor=1           # Delta pattern phasing
)

constellation_assets = walker_delta.generate_assets(
    base_name="Iridium",
    start_epoch=scenario.start_time,
    include_spares=True        # Include spare satellites
)
```

### Streets-of-Coverage

Streets-of-Coverage patterns provide continuous coverage along specific latitudes:

```python
from ephemerista.constellation.design import StreetOfCoverage

street_pattern = StreetOfCoverage(
    latitude_coverage=(-70, 70),    # Coverage latitude bounds
    longitude_spacing=22.5,     # Longitude separation in degrees
    inclination=99.5,           # Sun-synchronous inclination
    altitude=700,                # LEO altitude in km
    local_time_ascending_node=10.5  # LTAN in hours
)

street_constellation = street_pattern.generate_assets(
    base_name="EarthObserver",
    start_epoch=scenario.start_time
)
```

### Custom Constellation Design

```python
from ephemerista.constellation.plane import OrbitalPlane

# Define custom orbital planes
plane_1 = OrbitalPlane(
    inclination=98.7,
    raan=0.0,
    satellites_per_plane=5,
    altitude=600,
    true_anomaly_offset=0.0
)

plane_2 = OrbitalPlane(
    inclination=98.7,
    raan=120.0,
    satellites_per_plane=5,
    altitude=600,
    true_anomaly_offset=72.0  # Phase offset
)

# Combine into custom constellation
custom_constellation = [plane_1, plane_2]
```

### Constellation Visualization

#### GUI: 3D Constellation Display

The 3D viewer displays:
- All constellation satellites simultaneously
- Orbital planes and satellite distribution
- Ground track patterns
- Real-time constellation evolution

*[SCREENSHOT PLACEHOLDER: 3D visualization of a Walker constellation showing multiple orbital planes]*

## Coverage Analysis

### Overview

Coverage analysis determines how well a satellite constellation covers geographic areas of interest over time.

```{seealso}
For complete coverage analysis API documentation, see {doc}`../api/analysis/coverage`.
```

### Defining Areas of Interest

#### GUI: Area Definition

1. Click **"Add Area of Interest"** in the scenario configuration
2. Define the geographic region:
   - **GeoJSON Import**: Upload polygon definitions
   - **Manual Definition**: Enter coordinate points
   - **Shape Tools**: Use built-in drawing tools

*[SCREENSHOT PLACEHOLDER: Area of interest definition interface with map view]*

#### Python: Area Definition

```{seealso}
For area shapes API documentation, see {doc}`../api/coords/shapes`.
```

```python
from ephemerista.coords.shapes import CircularArea, RectangularArea

# Circular coverage area
circular_area = CircularArea(
    center_latitude=40.7128,   # New York City
    center_longitude=-74.0060,
    radius=500.0,
    name="NYC Metropolitan Area"
)

# Rectangular coverage area
rectangular_area = RectangularArea(
    southwest_corner=(25.0, -125.0),  # lat, lon
    northeast_corner=(49.0, -66.0),   # Continental US
    name="Continental United States"
)

scenario.add_area_of_interest(circular_area)
scenario.add_area_of_interest(rectangular_area)
```

### Running Coverage Analysis

#### GUI: Coverage Configuration

1. Select **"Coverage"** analysis type
2. Specify parameters:
   - **Temporal Resolution**: Time step for coverage calculation
   - **Minimum Elevation**: Required satellite elevation
   - **Minimum Contact Duration**: Required visibility time

*[SCREENSHOT PLACEHOLDER: Coverage analysis configuration panel]*

#### Python: Coverage Calculation

```python
from ephemerista.analysis.coverage import Coverage

# Create coverage analyzer
coverage_analyzer = Coverage(
    scenario,
    temporal_resolution=300,  # 5-minute intervals
    spatial_resolution=1.0,       # 1-degree grid
    min_elevation=10.0,
    include_eclipse_periods=False
)

# Compute coverage
coverage_results = coverage_analyzer.calculate()

# Access coverage statistics
for area_id, area_results in coverage_results.items():
    area_name = area_results.area_name
    coverage_percentage = area_results.coverage_percentage
    max_gap_hours = area_results.max_gap_duration / 3600
    mean_revisit_time_hours = area_results.mean_revisit_time / 3600
    
    print(f"Area: {area_name}")
    print(f"Coverage: {coverage_percentage:.1f}%")
    print(f"Max gap: {max_gap_hours:.1f} hours")
    print(f"Mean revisit: {mean_revisit_time_hours:.1f} hours")
```

### Understanding Coverage Results

#### Coverage Metrics

- **Coverage Percentage**: Fraction of area covered
- **Maximum Gap**: Longest period without coverage
- **Revisit Time**: Time between successive coverage events
- **Mean Access Duration**: Average contact time

*[SCREENSHOT PLACEHOLDER: Coverage metrics summary table]*

#### Coverage Visualization

- **Spatial Coverage Maps**: Geographic distribution of coverage
- **Temporal Coverage**: Coverage availability over time
- **Gap Analysis**: Identification of coverage holes

*[SCREENSHOT PLACEHOLDER: Coverage map showing colored regions indicating coverage levels]*

## Navigation Analysis

### GNSS Configuration

Navigation analysis evaluates the performance of Global Navigation Satellite Systems (GNSS).

```{seealso}
For complete navigation analysis API documentation, see {doc}`../api/analysis/index`.
```

### Setting Up Navigation Analysis

#### GUI: Navigation Configuration

1. Configure navigation satellite constellation
2. Set up ground-based observers (users)
3. Define geometric dilution of precision requirements

*[SCREENSHOT PLACEHOLDER: Navigation analysis setup with GNSS constellation]*

#### Python: Navigation Setup

```python
from ephemerista.analysis.navigation import Navigation
from ephemerista.constellation.design import WalkerStar

# Create GPS-like constellation
gps_constellation = WalkerStar(
    num_satellites=24,
    num_planes=6,
    inclination=55.0,
    altitude=20200,
    phasing_parameter=0
)

# Generate navigation satellites
nav_satellites = gps_constellation.generate_assets(
    base_name="GPS_SV",
    start_epoch=scenario.start_time
)

# Add to scenario
for satellite in nav_satellites:
    scenario.add_asset(satellite)

# Create navigation analyzer
nav_analyzer = Navigation(scenario)
```

### Dilution of Precision (DOP) Analysis

#### DOP Metrics

- **GDOP**: Geometric Dilution of Precision
- **PDOP**: Position Dilution of Precision  
- **HDOP**: Horizontal Dilution of Precision
- **VDOP**: Vertical Dilution of Precision
- **TDOP**: Time Dilution of Precision

*[SCREENSHOT PLACEHOLDER: DOP analysis results showing all DOP values over time]*

#### Python: DOP Calculation

```python
# Compute navigation performance
nav_results = nav_analyzer.calculate()

# Access DOP values
for observer_id, observer_results in nav_results.items():
    observer_name = observer_results.observer_name
    
    # DOP time series
    times = observer_results.times
    gdop = observer_results.gdop        # Geometric DOP
    pdop = observer_results.pdop        # Position DOP
    hdop = observer_results.hdop        # Horizontal DOP
    vdop = observer_results.vdop        # Vertical DOP
    tdop = observer_results.tdop        # Time DOP
    
    # Satellite visibility
    visible_satellites = observer_results.visible_satellites
    
    print(f"Observer: {observer_name}")
    print(f"Mean GDOP: {np.mean(gdop):.2f}")
    print(f"Mean visible satellites: {np.mean(visible_satellites):.1f}")
```

### Navigation Performance Assessment

#### Position Accuracy

- **Horizontal Accuracy**: Expected horizontal position error
- **Vertical Accuracy**: Expected vertical position error
- **3D Position Accuracy**: Overall position uncertainty

#### Service Availability

- **Availability Percentage**: Time with adequate satellite geometry
- **Service Outages**: Periods with insufficient satellites
- **Performance Degradation**: Times with poor geometry

*[SCREENSHOT PLACEHOLDER: Service availability timeline plot]*

## Visualization and Data Export

### GUI: 3D Visualization

#### Visualization Controls

- **Orbit**: Click and drag to rotate view
- **Pan**: Right-click and drag to pan
- **Zoom**: Mouse wheel or pinch to zoom
- **Reset View**: Return to default perspective

*[SCREENSHOT PLACEHOLDER: 3D viewer with visible camera control indicators]*

#### Asset Tracking

Ephemerista supports antenna tracking, where assets can automatically point their antennas towards other assets or constellation members. This feature is essential for maintaining communication links between spacecraft and ground stations.

##### Configuring Tracking in the GUI

In the **Assets** tab of the scenario configuration:

1. **Navigate to Antenna Tracking Configuration**: Found at the bottom of each asset's configuration panel
2. **Set Pointing Error**: Define the tracking accuracy in degrees (typical values: 0.1° for high-precision systems, 0.5-1.0° for standard systems)
3. **Select Tracked Assets**: Choose individual assets from the list that this asset's antennas should track
4. **Select Tracked Constellations**: Choose constellations to track any member spacecraft

*[SCREENSHOT PLACEHOLDER: Asset form showing tracking configuration section with selected assets and constellations]*

##### Tracking Behavior

- **Direct Tracking**: When an asset directly tracks another asset, the antenna maintains pointing with the specified error
- **Multi-Target Tracking**: When tracking multiple assets, the antenna points to the closest tracked target
- **Constellation Tracking**: Assets can track any member of a constellation that communicates with them
- **Automatic Selection**: The system automatically selects the best target when multiple options are available

#### Display Elements

- **Earth Model**: High-resolution Earth texture
- **Satellite Models**: 3D satellite representations
- **Orbital Paths**: Historical and predicted trajectories
- **Ground Station Markers**: Fixed Earth locations
- **Visibility Cones**: Ground station coverage areas
- **Coverage Areas**: Color-coded coverage regions

#### Time Controls

- **Play/Pause**: Start/stop time animation
- **Time Slider**: Manually control simulation time
- **Speed Control**: Adjust animation speed
- **Time Display**: Current simulation time

*[SCREENSHOT PLACEHOLDER: Time control interface at bottom of 3D viewer]*

### Python: Plotting and Visualization

```{seealso}
For complete plotting API documentation, see {doc}`../api/plot/index`.
```

```python
from ephemerista.plot.ground_track import plot_ground_track
from ephemerista.plot.visibility import plot_visibility_pass

# Plot ground track with visibility
fig = plot_ground_track(
    scenario=scenario,
    asset_names=["Earth Observer 1"],
    show_ground_stations=True,
    show_visibility_circles=True
)

# Plot individual pass details
pass_plot = plot_visibility_pass(
    pass_data=passes[0],
    show_elevation=True,
    show_azimuth=True,
    show_range=True
)
```

### Data Export

#### GUI: Export Options

1. Click the **"Export"** button
2. Choose export format:
   - **JSON**: Native Ephemerista format
   - **CSV**: Tabular data for spreadsheet analysis
   - **CCSDS**: Standard space data formats

*[SCREENSHOT PLACEHOLDER: Export dialog with format options]*

#### Python: Data Export

```python
# Export scenario
scenario.save("mission_scenario.json")

# Export analysis results to CSV
visibility_results.to_csv("visibility_passes.csv")
coverage_results.to_csv("coverage_statistics.csv")

# Export to CCSDS format
from ephemerista.io.ccsds import export_oem
export_oem(ensemble, "satellite_ephemeris.oem")
```

## Advanced Features

### Custom Analysis Modules (Python)

Create custom analysis modules by extending the base class:

```python
from ephemerista.analysis.base import AnalysisModule

class CustomInterferenceAnalysis(AnalysisModule):
    """Custom interference analysis implementation."""
    
    def __init__(self, interference_threshold=-120.0):
        super().__init__()
        self.interference_threshold = interference_threshold
    
    def calculate(self):
        """Perform custom interference analysis."""
        results = {}
        
        for asset in self.scenario.all_assets:
            if hasattr(asset, 'communication_systems'):
                # Analyze interference for each communication system
                interference_data = self._compute_interference(asset)
                results[asset.id] = interference_data
        
        return results
    
    def _compute_interference(self, asset):
        """Compute interference levels."""
        # Implementation details
        pass

# Use custom analysis
custom_analyzer = CustomInterferenceAnalysis(
    interference_threshold=-115.0
)
custom_results = custom_analyzer.calculate()
```

### Parallel Processing

```python
# Configure parallel processing
from ephemerista.parallel import ParallelProcessor
import multiprocessing

processor = ParallelProcessor(
    num_processes=multiprocessing.cpu_count(),
    chunk_size="auto",              # Automatic load balancing
    memory_limit_gb=8.0             # Memory usage limit
)

# Use parallel processing in analysis
visibility_analyzer = Visibility(scenario, parallel=True)
```

### Integration with External Tools

#### CCSDS Standards Support

```python
from ephemerista.io.ccsds import OemExporter, AemExporter

# Export to CCSDS OEM format
oem_exporter = OemExporter()
oem_file = oem_exporter.export_ensemble(
    ensemble, 
    output_file="satellite_ephemeris.oem"
)

# Export attitude data (AEM)
aem_exporter = AemExporter()
aem_file = aem_exporter.export_attitude(
    attitude_data,
    output_file="satellite_attitude.aem"
)
```

## Examples and Tutorials

### Complete Mission Analysis Example

```python
#!/usr/bin/env python3
"""
Complete Earth Observation Mission Analysis Example

This example demonstrates a full mission analysis workflow including:
- Constellation design
- Coverage analysis  
- Communication link budgets
- Navigation performance assessment
"""

import ephemerista
from ephemerista import Scenario
from ephemerista.time import Epoch, TimeScale
from ephemerista.constellation.design import WalkerStar
from ephemerista.assets import GroundStation
from ephemerista.analysis.visibility import Visibility
from ephemerista.analysis.coverage import Coverage
from ephemerista.analysis.link_budget import LinkBudget
from ephemerista.analysis.navigation import Navigation
from datetime import datetime, timezone

# Initialize Ephemerista
ephemerista.init(
    eop_file="data/finals2000A.all.csv",
    ephemeris_file="data/de440s.bsp"
)

# Create scenario
scenario = Scenario(
    name="Earth Observation Mission",
    start_time=Epoch.from_datetime(
        datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc),
        TimeScale.UTC
    ),
    end_time=Epoch.from_datetime(
        datetime(2024, 6, 8, 0, 0, 0, tzinfo=timezone.utc),
        TimeScale.UTC
    ),
    time_step=300.0  # 5-minute intervals
)

# Design constellation
constellation = WalkerStar(
    num_satellites=12,
    num_planes=3,
    inclination=98.7,  # Sun-synchronous
    altitude=700,
    phasing_parameter=1
)

# Generate constellation assets
satellites = constellation.generate_assets(
    base_name="EarthObs",
    start_epoch=scenario.start_time
)

# Add satellites to scenario
for satellite in satellites:
    scenario.add_asset(satellite)

# Add ground stations
ground_stations = [
    GroundStation(
        name="Alaska Station",
        latitude=64.8,
        longitude=-147.7,
        altitude=200.0,
        minimum_elevation=10.0
    ),
    GroundStation(
        name="Svalbard Station", 
        latitude=78.2,
        longitude=15.4,
        altitude=100.0,
        minimum_elevation=5.0
    )
]

for station in ground_stations:
    scenario.add_asset(station)

# Define coverage areas
from ephemerista.coords.shapes import RectangularArea

arctic_area = RectangularArea(
    southwest_corner=(66.5, -180.0),  # Arctic Circle
    northeast_corner=(90.0, 180.0),
    name="Arctic Region"
)

scenario.add_area_of_interest(arctic_area)

# Perform analyses
print("Running mission analysis...")

# 1. Visibility Analysis
print("Computing visibility...")
visibility_analyzer = Visibility(scenario)
visibility_results = visibility_analyzer.calculate()

# 2. Coverage Analysis  
print("Computing coverage...")
coverage_analyzer = Coverage(scenario)
coverage_results = coverage_analyzer.calculate()

# 3. Link Budget Analysis
print("Computing link budgets...")
link_budget_analyzer = LinkBudget(scenario)
link_budget_results = link_budget_analyzer.calculate()

# 4. Navigation Performance
print("Computing navigation performance...")
nav_analyzer = Navigation(scenario)
nav_results = nav_analyzer.calculate()

# Generate reports
print("\n=== MISSION ANALYSIS RESULTS ===\n")

# Visibility Summary
total_passes = sum(len(passes) for observer_results in visibility_results.values() 
                  for passes in observer_results.values())
print(f"Total visibility passes: {total_passes}")

# Coverage Summary
for area_id, area_results in coverage_results.items():
    print(f"Coverage for {area_results.area_name}: {area_results.coverage_percentage:.1f}%")
    print(f"Maximum gap: {area_results.max_gap_duration/3600:.1f} hours")

# Link Budget Summary
successful_links = sum(1 for link_data in link_budget_results.values() 
                      if link_data.link_margin > 0)
total_links = len(link_budget_results)
print(f"Successful communication links: {successful_links}/{total_links}")

# Navigation Summary
for observer_id, results in nav_results.items():
    mean_gdop = sum(results.gdop) / len(results.gdop)
    print(f"Mean GDOP for {results.observer_name}: {mean_gdop:.2f}")

print("\nMission analysis completed successfully!")
```

### Antenna Tracking Example

```python
"""
Antenna Tracking Configuration Example

This example demonstrates how to configure antenna tracking between
spacecraft and ground stations for optimal communication links.
"""

import ephemerista
from ephemerista import Scenario
from ephemerista.assets import Asset, GroundStation, Spacecraft
from ephemerista.constellation.design import WalkerDelta
from ephemerista.analysis.link_budget import LinkBudget

# Initialize Ephemerista
ephemerista.init()

# Create a scenario with ground stations and satellites
scenario = Scenario(name="Tracking Demo")

# Add ground stations
gs_washington = Asset(
    name="Washington DC",
    model=GroundStation.from_lla(
        longitude=-77.0369,
        latitude=38.9072,
        altitude=0.0
    )
)

gs_madrid = Asset(
    name="Madrid DSN",
    model=GroundStation.from_lla(
        longitude=-4.2477,
        latitude=40.4316,
        altitude=840.0
    )
)

# Create a LEO constellation
constellation = WalkerDelta(
    name="LEO Comm Constellation",
    nsats=8,
    nplanes=2,
    inclination=45.0,
    altitude=550.0,
    phasing=1
)

# Add assets to scenario
scenario.add_asset(gs_washington)
scenario.add_asset(gs_madrid)
scenario.add_constellation(constellation)

# Configure tracking - Ground stations track any constellation member
gs_washington.track(constellation_ids=constellation.constellation_id)
gs_madrid.track(constellation_ids=constellation.constellation_id)

# Configure satellites to track multiple ground stations
# They will automatically select the closest one
constellation_assets = constellation.assets
for satellite in constellation_assets:
    satellite.track(asset_ids=[
        gs_washington.asset_id,
        gs_madrid.asset_id
    ])
    # Set high-precision tracking
    satellite.pointing_error = 0.1  # degrees

# Alternative: Direct asset tracking
# Track a specific satellite from a ground station
specific_satellite = constellation_assets[0]
gs_washington.track(asset_ids=[specific_satellite.asset_id])

# Analyze link budgets with tracking
link_budget = LinkBudget(scenario=scenario)
results = link_budget.analyze()

# The link budget will now use the configured tracking
# to calculate accurate antenna pointing angles
for link in results[gs_washington, specific_satellite]:
    for stat in link.stats:
        print(f"Time: {stat.time}")
        print(f"  TX Angle: {stat.tx_angle.degrees:.2f}°")
        print(f"  RX Angle: {stat.rx_angle.degrees:.2f}°")
        print(f"  Link Margin: {stat.margin:.2f} dB")
```

## Troubleshooting and Reference

### Common Issues

#### Propagation Errors

**Invalid TLE Format**
- Ensure proper two-line element formatting
- Check TLE epoch dates are appropriate for analysis period

**Numerical Integration Issues**
- Verify initial state vectors are realistic
- Check force model parameters

#### Visualization Problems

**WebGL Support**
- Ensure browser supports WebGL
- Update graphics drivers if needed

**Performance Issues**
- Reduce number of displayed satellites
- Lower temporal resolution for long analyses

#### Analysis Failures

**Insufficient Data**
- Ensure all required parameters are specified
- Check that assets have necessary properties

**Memory Limitations**
- Reduce analysis duration or temporal resolution
- Use parallel processing for large scenarios

### Performance Optimization

#### Large Constellations
- Use temporal sampling to reduce computation
- Focus analysis on specific time windows
- Consider constellation subsets for initial analysis

#### Complex Scenarios
- Start with simplified configurations
- Gradually add complexity
- Use quick setup options when possible

### Getting Help

#### Documentation
- **User Manual**: This document
- **API Documentation**: {doc}`../api/index`
- **Examples**: [Examples and Tutorials](#examples-and-tutorials) and {doc}`tutorials`

#### Support Resources
- **Issue Reporting**: Bug reports and feature requests
- **Community Forums**: User discussions and solutions
- **Technical Support**: Direct assistance for complex issues

---

*This unified user manual provides comprehensive guidance for using both the Ephemerista GUI and Python API. For the latest updates and additional resources, visit the project repository.*