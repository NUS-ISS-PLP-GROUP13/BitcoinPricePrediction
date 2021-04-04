### This is the running code of Bitcoin price prediction and related topic modelling system 

* **Required packages for SYSTEM:**
  * pytorch
  * transformer


#### To run the system, we need to download other larger files like model weights and database files to support the whole system

* Download model1a pre-trained model parameters and weights [here is the link](https://1drv.ms/u/s!AhXWl5uPYwBog22EU8lat_QHQRgY?e=1Pkt25)  and put it into filepath Controller/Model1/
* Download database sql file [here is the link](https://1drv.ms/u/s!AhNOBSYLzOAhkiuSG5BtMddjuxfW?e=urflpg) 
* After downloading the sql file we need to modify the file in Controller/DB/DB_basic.py to customize the configure to local settings.
 ``` 
db = {
    "host": 'localhost',
    "user": "root",
    "pwd": "",
    "db_name": "bitcoin"
      }
 ```
 * run the downloaded sql file to construct the whole database
