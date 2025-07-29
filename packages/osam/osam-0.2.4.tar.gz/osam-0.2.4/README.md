<div align="center">
  <img alt="logo" height="200px" src="https://github.com/wkentaro/osam/raw/main/.readme/icon.png" >
  <h1>Osam</h1>
  <p>
    Get up and running with promptable vision models locally.
  </p>
  <br>
  <br>
  <br>
</div>

*Osam* (/oʊˈsɑm/) is a tool to run open-source promptable vision models locally
(inspired by [Ollama](https://github.com/ollama/ollama)).

*Osam* provides:

- **Promptable Vision Models** - Segment Anything Model (SAM), EfficientSAM, YOLO-World;
- **Local APIs** - CLI & Python & HTTP interface;
- **Customization** - Host custom vision models.


## Installation

### Pip

<a href="https://pypi.org/project/osam"><img src="https://img.shields.io/pypi/pyversions/osam.svg"></a>
<a href="https://pypi.python.org/pypi/osam"><img src="https://img.shields.io/pypi/v/osam.svg"></a>

```bash
pip install osam
```

**For `osam serve`**:

```bash
pip install osam[serve]
```

## Quickstart

To run with EfficientSAM:

```bash
osam run efficientsam --image <image_file>
```

To run with YOLO-World:

```bash
osam run yoloworld --image <image_file>
```

## Model library

Here are models that can be downloaded:

| Model             | Parameters | Size  | Download                     |
|-------------------|------------|-------|------------------------------|
| SAM 100M          | 94M        | 100MB | `osam run sam:100m`          |
| SAM 300M          | 313M       | 310MB | `osam run sam:300m`          |
| SAM 600M          | 642M       | 630MB | `osam run sam`               |
| SAM2 Tiny         | 39M        | 150MB | `osam run sam2:tiny`         |
| SAM2 Small        | 46M        | 170MB | `osam run sam2:small`        |
| SAM2 BasePlus     | 82M        | 300MB | `osam run sam2`              |
| SAM2 Large        | 227M       | 870MB | `osam run sam2:large`        |
| EfficientSAM 10M  | 10M        | 40MB  | `osam run efficientsam:10m`  |
| EfficientSAM 30M  | 26M        | 100MB | `osam run efficientsam`      |
| YOLO-World XL     | 168M       | 640MB | `osam run yoloworld`         |

PS. `sam`, `efficientsam` is equivalent to `sam:latest`, `efficientsam:latest`.

## Usage

### CLI

```bash
# Run a model with an image
osam run efficientsam --image examples/_images/dogs.jpg > output.png

# Get a JSON output
osam run efficientsam --image examples/_images/dogs.jpg --json
# {"model": "efficientsam", "mask": "..."}

# Give a prompt
osam run efficientsam --image examples/_images/dogs.jpg \
  --prompt '{"points": [[1439, 504], [1439, 1289]], "point_labels": [1, 1]}' \
  > efficientsam.png
osam run yoloworld --image examples/_images/dogs.jpg --prompt '{"texts": ["dog"]}' \
  > yoloworld.png
```

<img src="https://github.com/wkentaro/osam/raw/main/examples/_images/dogs.jpg" width="30%"> <img src="https://github.com/wkentaro/osam/raw/main/.readme/dogs_efficientsam.png" width="30%"> <img src="https://github.com/wkentaro/osam/raw/main/.readme/dogs_yoloworld.png" width="30%">  
<i>Input and output images ('dogs.jpg', 'efficientsam.png', 'yoloworld.png').</i>

### Python

```python
import osam.apis
import osam.types

request = osam.types.GenerateRequest(
    model="efficientsam",
    image=np.asarray(PIL.Image.open("examples/_images/dogs.jpg")),
    prompt=osam.types.Prompt(points=[[1439, 504], [1439, 1289]], point_labels=[1, 1]),
)
response = osam.apis.generate(request=request)
PIL.Image.fromarray(response.mask).save("mask.png")
```
<img src="https://github.com/wkentaro/osam/raw/main/examples/_images/dogs.jpg" width="35%"> <img src="https://github.com/wkentaro/osam/raw/main/.readme/dogs_efficientsam_mask.png" width="35%">  
<i>Input and output images ('dogs.jpg', 'mask.png').</i>

### HTTP

```bash
# pip install osam[serve]  # required for `osam serve`

# Get up the server
osam serve

# POST request
curl 127.0.0.1:11368/api/generate -X POST \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"efficientsam\", \"image\": \"$(cat examples/_images/dogs.jpg | base64)\"}" \
  | jq -r .mask | base64 --decode > mask.png
```
