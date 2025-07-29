import datetime
import pyarrow as pa
import pyarrow.flight as fl
import os
import requests
import pandas
import json
import re
import datetime
import urllib
from dotenv import load_dotenv

load_dotenv()
req = requests.Session()
"""
Available environment variables:
AUTH_SESSION          : an API authentication token
TLS_VERIFICATION_PATH : path to TLS cerficate authority (CA) file
TLS_CLIENT_CERT_PATH  : path to TLS client certificate file
"""

auth_session = os.environ.get("AUTH_SESSION", None)
if auth_session: 
    # print("Setting session from AUTH_SESSION")
    req.cookies.update({"id": auth_session})
tls_verification = os.environ.get("TLS_VERIFICATION_PATH", None)
if tls_verification != None: 
    # print("Found TLS Verification Path")
    # print("Optionally disable TLS Verification")
    tls_verification = False if tls_verification == "False" else tls_verification
    req.verify = tls_verification
tls_cert = os.environ.get("TLS_CLIENT_CERT_PATH", None)
if tls_cert != None: 
    req.cert = tls_cert


def sample(pipeline_id: str, host=None, auth_session=None, genuine=10000, fraud=-1, from_days=None, to_days=None):
    """Returns a data sample for machine learning of [data, fraud_label].
       "data" and "fraud_label" have the same length of genuine + fraud. 
       "data" doesn't contain the fraud label 
       and "fraud_label" only contains the fraud label."""
    data = _query_json_data(pipeline_id, host, auth_session, genuine, fraud, from_days, to_days)
    data = json.loads(data.text)
    fraud_field = data["fraud_field"]
    data = pandas.json_normalize(data["data"])
    data = _convert_categories_and_timestamps(data)

    if fraud_field in data:
        data_fraud = data[fraud_field].astype("int")
        data.drop(columns=[fraud_field], inplace=True)
    else:
        if len(data) == 0: 
            print(f"Queried data is empty. Cannot continue with empty data.")
            raise Exception("No data found")
        else: 
            print(f"Fraud field '{fraud_field}' missing in data:")
            print(data)
            raise Exception("No fraud data found")
    return data, data_fraud

def _query_json_data(pipeline_id: str, host=None, auth_session=None, genuine=10000, fraud=-1, from_days=None, to_days=None):
    if host is None:
        host = os.environ.get("UI_HOST", None)
    if host is None:
        raise Exception(
            "The FraudAverse UI server host must be either passed as the `host` argument or set in the `UI_HOST` environment variable."
        )
    if (auth_session): 
        req.cookies.update({"id": auth_session})
    query = '{}'
    if from_days != None:
        now = datetime.datetime.now(datetime.timezone.utc)
        if to_days != None: 
            query = { "$and": [ 
                    {"__timestamp_field": {"$gt": str(now - datetime.timedelta(from_days)) } },
                    {"__timestamp_field": {"$lt": str(now - datetime.timedelta(to_days)) } },
                    ] }
        else:
            query = {"__timestamp_field": {"$gt": str(now - datetime.timedelta(from_days)) } }
        query = urllib.parse.quote(json.dumps(query))
    data = req.get(
        host + "/investigation/extern_api/sample/" + pipeline_id + f"/query/{query}/genuine/{genuine}/fraud/{fraud}"
    )
    return data

def _convert_categories_and_timestamps(data: pandas.DataFrame):
    try:
        if "rulesFired" in data:    
            # drop rulesFired as it usually is a list
            data = data.drop(columns=["rulesFired"])
        if "_id.$oid" in data:
            data = data.drop(columns=["_id.$oid"])
    except Exception as e:
        print(e)
    drop_frames = []
    # convert strings and objects to categories, convert dates to timestamps
    for frame in data:
        try:
            if data[frame].dtype == "datetime64[ns, UTC]" and re.search('timestamp', frame, re.IGNORECASE):
                print(data[frame].dtype )
                data[frame] = data[frame].astype("uint64")
            if data[frame].dtype == "object" and re.search('timestamp', frame, re.IGNORECASE):
                if re.search('\\$date\\.\\$numberLong', frame):
                    data[frame.replace(".$date.$numberLong", "")] = data[frame].astype("uint64")
                    drop_frames.append(frame)
                else:
                    data[frame] = ((pandas.to_datetime(data[frame], utc=True) - pandas.Timestamp("1970-01-01", tz=datetime.timezone.utc)) // pandas.Timedelta("1s")).astype("uint64")
            elif data[frame].dtype == "object":
                data[frame] = data[frame].astype('category')
            if data[frame].dtype == "String":
                data[frame] = data[frame].astype('category')
        except Exception as e:
            print(f"Error in {frame}:", e)
            drop_frames.append(frame)
    data.drop(columns=drop_frames, inplace=True)
    return data

def get_categories(pd_dataframe: pandas.DataFrame):
    """Extracts all categories from pandas dataframe into single json."""
    categories = json.loads("{}")
    for frame in pd_dataframe:
        if pd_dataframe[frame].dtype == "category":
            cats = pandas.DataFrame({frame: pd_dataframe[frame].cat.categories})
            pd_dataframe[frame]
            categories[frame] = json.loads(cats.to_json())[frame]
    return categories
    

def persist(pipeline_id, compute_id, model_name, model, categories = "", host=None, auth_session=None):
    """ Persists a model in a scoring compute referenced by a pipeline and compute id
        Parameters
        ----------
        pipeline_id : str
            The pipeline id of the pipeline that should get modified. 
            The id is displayed in the url of the ui: `pipeline/{pipeline_id}/`
        compute_id : str
            The existing scoring compute that will receive the new model.
            The id is displayed in the url of the ui: `compute/{compute_id}/`
        model_name : str
            File name that should be displayed
        model : str
            The model as string in xgboost json format
        categories : str
            (optional) A json string of all categories that were used during training in following format
            {"attr1": { "0": "val_1", "1": "val_2"}, "attr2": { "0": "a", "b": "c"} }
    """
    
    if host is None:
        host = os.environ.get("UI_HOST", None)
    if host is None:
        raise Exception(
            "The FraudAverse UI server host must be either passed as the `host` argument or set in the `UI_HOST` environment variable."
        )
    if (auth_session): 
        req.cookies.update({"id": auth_session})

    try:
        response = req.put(
            host + "/processing/pipeline/" + pipeline_id + "/compute/" + compute_id + "/",
            json={"name": model_name, "model": model, "categories": categories},
        )
        response.raise_for_status()  # Raises an HTTPError if the status code is 4xx, 5xx
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}")

    return response.text