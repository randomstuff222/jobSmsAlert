import requests
import os
from smsAlert import smsAlert
import time
import logging
import pickle

#URL_TO_MONITOR = 'http://127.0.0.1:8080/'
MSFT_URL = "https://gcsservices.careers.microsoft.com/search/api/v1/search?q=software%20engineer&lc=Redmond%2C%20Washington%2C%20United%20States&lc=United%20States&ws=Up%20to%20100%25%20work%20from%20home&l=en_us&pg=1&pgSz=20&o=Recent&flt=true"

AMAZON_URL = "https://www.amazon.jobs/en/search.json?schedule_type_id%5B%5D=Full-Time&normalized_country_code%5B%5D=USA&normalized_state_name%5B%5D=Washington&normalized_city_name%5B%5D=Redmond&normalized_city_name%5B%5D=Seattle&radius=24km&facets%5B%5D=normalized_country_code&facets%5B%5D=normalized_state_name&facets%5B%5D=normalized_city_name&facets%5B%5D=location&facets%5B%5D=business_category&facets%5B%5D=category&facets%5B%5D=schedule_type_id&facets%5B%5D=employee_class&facets%5B%5D=normalized_location&facets%5B%5D=job_function_id&facets%5B%5D=is_manager&facets%5B%5D=is_intern&offset=0&result_limit=10&sort=recent&latitude=&longitude=&loc_group_id=&loc_query=&base_query=&city=&country=&region=&county=&query_options=&category%5B%5D=software-development&"

#This function is to access the job list by using the lsit path of nested parameters feed in the check_file() function
# dictionary {list}: The response from the request
# keys {list}: The path to get to the job list using nested parameters
def access_nested_dictionary(dictionary:list, keys:list):
    current_item = dictionary
    for key in keys:
        if key in current_item:
            current_item = current_item[key]
        else:
            return None
    return current_item

# This function takes the following parameters:
# link: the link which is going to be requested (along with the filters).
# file_path {str}: this is the file name on the local machine in which it will save the ids to check (it needs to be a pkl file).
# job_path {list}: an array containing each name of the nested parameters in order to access where the list of jobs is saved (example: ["operationResult", "result", "jobs"] for MSFT)
# Each company request response has different names for the parameters, so the followings are to specify
# job_id_name {str}: the id of the job in the response.
# job_title_name {str}: the title of the job in the response.

def check_file(link:str, file_path:str, job_path:list, job_id_name:str, job_title_name:str):
    response_API = requests.get(link).json()
    collected_list = []
    previous_response = []
    responseAPI_jobs = access_nested_dictionary(response_API, job_path)
    #save/collect the list of jobs from the request 
    for i in responseAPI_jobs:
        collected_list.append(i[job_id_name])
    if not os.path.exists(file_path):
        open(file_path, 'w+').close()

    with open(file_path, "rb") as file:
        try:
            previous_response = pickle.load(file)

        #if file is empty, make the collected list to be the first one
        except EOFError:
            previous_response = collected_list[:]

    #the difference will always return the new element coming from the collected_list, which will be the new job added

    diff_elements = set(collected_list) - set(previous_response)
    #if there aren't new job ids added to the list, there aren't any new jobs posted
    if not diff_elements:
        return None
    #if there is a new job id, then write it on the file, and then return the newly added job id and title
    with open(file_path, "wb") as file:
        pickle.dump(collected_list, file)
    filtered_objects = [f'{obj[job_id_name]} = {obj[job_title_name]}\n\n' for obj in responseAPI_jobs if obj[job_id_name] in diff_elements]
    return ''.join(filtered_objects)

def main():
    log = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    log.info("Running Website Monitor")
    az_results = check_file(AMAZON_URL, "previous_amazon_content.pkl", ["jobs"], 'id_icims', "title")
    msft_result = check_file(MSFT_URL, "previous_microsoft_content.pkl", ["operationResult","result","jobs"], 'jobId', "title")
    while True:
        try:
            if msft_result:
                log.info("WEBPAGE WAS CHANGED ON MICROSOFT.")
                smsAlert("Microsoft", msft_result)

            if az_results:
                log.info("WEBPAGE WAS CHANGED ON MICROSOFT.")
                smsAlert("Amazon", az_results)
            else:
                log.info("Webpages were not changed.")
        except:
            log.info("Error checking website.")
            
        time.sleep(60)


if __name__ == "__main__":
    main()