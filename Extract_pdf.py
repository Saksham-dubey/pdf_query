import requests
data = requests.get("https://api.openalex.org/works?filter=institutions.id:I4210130631")

response_data = data.json()
response_data = response_data['results']
# len(response_data)
print(response_data[0]['primary_location']['pdf_url'])

# print(response_data[0]['pdf_url'])
url_list = []
for i in response_data:
    print(i['primary_location']['pdf_url'])
    url_list.append(i['primary_location']['pdf_url'])
len(url_list)
# with open('response_data.txt', 'w',encoding='utf-8') as file:
#     file.write(str(response_data))
