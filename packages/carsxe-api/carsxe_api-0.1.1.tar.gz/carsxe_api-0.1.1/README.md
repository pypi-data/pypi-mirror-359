# CarsXE API PIP V1

CarsXE is a powerful, easy-to-use API that gives you instant access to a wide range of vehicle data, including specs, market value, license plate decoding, and more. Our API is designed to be fast, flexible, and scalable, so you can quickly and easily integrate it into your existing applications and services. With CarsXE, you can get the information you need, when you need it, and take your business to the next level.

For documentation see the `carsxe-api` [API docs](https://api.carsxe.com/docs).

## Get Started

To get started with the CarsXE API, follow these steps:

1. [Sign up](https://api.carsxe.com/register) for a CarsXE account, Add a [payment method](https://api.carsxe.com/dashboard/billing#payment-methods) to activate your subscription, get your API key.

2. Install the CarsXE pip package using the following command:

```bash
pip install carsxe-api
# or
conda install carsxe-api
```

3. Import the CarsXE API into your code using the following line:

```python
from carsxe_api import CarsXE
```

4. Use the init method to initialize the API and provide your API key:

```python
API_KEY = 'ABC123'
carsxe = CarsXE(API_KEY)
```

5. Use the various endpoint methods provided by the API to access the data you need.

## Usage

```python
vin = '123456789'

try:
  vehicle = carsxe.specs({"vin": vin})
  print(vehicle["input"]["vin"])
except Exception as error:
  print(f"Error: {error}")

```

## Endpoints

The CarsXE API provides the following endpoint methods:

### `specs`: This method allows you to get detailed specs for a specific vehicle, based on its VIN (vehicle identification number).

**Required:**

- vin

**Optional:**

- deepdata
- disableIntVINDecoding

---

### `int_vin_decoder_api`: This method allows you to decode international VINs for vehicles.

**Required:**

- vin

**Optional:**

- None

---

### `recalls`: This method allows you to get recall information for a specific vehicle by VIN.

**Required:**

- vin

**Optional:**

- None

---

### `plate_decoder`: This method allows you to decode a license plate number and get information about the vehicle it is registered to.

**Required:**

- plate
- country (always required except for US, where it is optional and defaults to 'US')

**Optional:**

- state
- district

> **Note:**
>
> - The `state` parameter is required only when applicable (for specific countries such as US, AU, CA, etc.).
> - For Pakistan (`country='pk'`), both `state` and `district` are required.

---

### `images`: This method allows you to get images for a specific vehicle, based on a variety of parameters.

**Required:**

- make
- model

**Optional:**

- year
- trim
- color
- transparent
- angle
- photoType
- size
- license

---

### `market_value`: This method allows you to get the current market value for a specific vehicle, based on its make, model, year, and other factors.

**Required:**

- vin

**Optional:**

- state

---

### `history`: This method allows you to get the history of a specific vehicle, including its ownership, accidents, and other events.

**Required:**

- vin

**Optional:**

- None

---

### `plate_image_recognition`: This method allows you to recognize a license plate from an image URL.

**Required:**

- upload_url

**Optional:**

- None

---

### `vin_ocr`: This method allows you to extract a VIN from an image URL using OCR.

**Required:**

- upload_url

**Optional:**

- None

---

### `year_make_model`: This method allows you to get information based on year, make, and model.

**Required:**

- year
- make
- model

**Optional:**

- trim

---

### `obd_codes_decoder`: This method allows you to decode an OBD code and get information about the code.

**Required:**

- code

**Optional:**

- None

To use any of these endpoint methods, call the method and provide the necessary parameters, as shown in the following examples:

```python
vin = '123456789'

# Get specs
vehicle = carsxe.specs({"vin": vin})

# Decode international VIN
intvin = carsxe.int_vin_decoder({"vin": vin})

# Get recalls
recalls = carsxe.recalls({"vin": vin})

# Get license plate decoder
decoded_plate = carsxe.plate_decoder({"plate": "7XER187", "state": "CA", "country": "US"})

# Get images
images = carsxe.images({"make": "BMW", "model": "X5", "year": "2019"})

# Get market value
marketvalue = carsxe.market_value({"vin": vin})

# Get history
history = carsxe.history({"vin": vin})

# Recognize license plate from image URL
plateimg = carsxe.plate_image_recognition({"upload_url": "https://api.carsxe.com/img/apis/plate_recognition.JPG"})

# Extract VIN from image URL using OCR
vinocr = carsxe.vin_ocr({"upload_url": "https://api.carsxe.com/img/apis/plate_recognition.JPG"})

# Get info by year, make, and model
yymm = carsxe.year_make_model({"year": "2012", "make": "BMW", "model": "5 Series"})

# Get Decode OBD Code
obdcode = carsxe.obd_codes_decoder({"code": "P0115"})
```

**In these examples, each endpoint method is called with the necessary parameters, and the results are returned through a callback function. The callback function receives two arguments: an error object (if an error occurred) and the data returned by the endpoint. The data can then be used in your code as needed.**

**Overall, the CarsXE API provides a range of powerful, easy-to-use tools for accessing vehicle data and integrating it into your applications and services. By using the endpoint methods provided by the API, you can quickly and easily get the information you need, when you need it, and take your business to the next level. Whether you are a developer looking for vehicle data for your applications, or a business owner looking to enhance your services with vehicle data, the CarsXE API has something to offer. Try it today and see how easy it is to access the vehicle data you need, without any hassle or inconvenience.**
