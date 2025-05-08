# 2D-Material-Search

Full suite of software tools for 2D material search platform with flake recognition. Intended for Spring 2025 UMN Senior Design Project *An automated 2D Material Search Platform*. Includes stage motor control, image stitching, and ML flake recognition tools.

## Project Overview

This project aims to automate the search process for 2D materials using a combination of hardware control, computer vision, and machine learning techniques. The system integrates multiple components to create a comprehensive solution for material scientists and researchers.

## Components

### MotorMover
- `MotorMover.py`: Main motor control interface
- `SlideAlign.py`: Slide alignment and positioning
- `ImageCapture.py`: Image acquisition from microscope
- `ConexCC.py`: Newport CONEX-CC controller interface
- `background.py`: Background processing utilities

### GUI
- `gui.py`: Main graphical user interface
- Features a clean, user-friendly interface with UMN branding

### NeuralNet
- Machine learning pipeline for flake recognition
- Training and testing scripts:
  - `step1_labeling.mlx`: Data labeling
  - `step2_data_generation.mlx`: Training data preparation
  - `step3_training.m`: Model training
  - `step4_testwithExampleImage.m`: Model testing
- Support scripts:
  - `image_resize.py`: Image preprocessing
  - `image_rename.py`: Dataset organization

### ImageStitch
- `stitching.py`: Image stitching implementation
- `blending.py`: Seamless image blending algorithms
- Organized image directories for different stitching scenarios

## Setup and Installation

1. Clone the repository
2. Install required dependencies:
   - Python 3.x
   - MATLAB (for NeuralNet components)
   - Required Python packages (listed in `requirements.txt`)
   - Required MATLAB toolboxes (listed in `requirements.txt`)

## Usage

1. Launch the GUI application
2. Configure motor settings and microscope parameters
    - For ease, slide wafer to 0,0 box in 0,0 location
    - Then fine tune using GUI
3. Run automated search
4. Prepare data for and run ML algorithm (exact process in `NeuralNet\instructions.txt`)
5. View and analyze results

## References
<a id="1">[1]</a> 
Semantic NN for pixel classification of 2D materials
- https://github.com/yafangy/Nanomaterial_DeepLearning

## License

See the [LICENSE](LICENSE) file for details.
