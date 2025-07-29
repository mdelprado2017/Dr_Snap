import requests
import app.consts_drscratch as consts
from lxml import etree


class Project:

    def __init__(self, xml_data):
        root = etree.fromstring(xml_data)
        self.id = root.xpath('//snapdata/@remixID')[0]
        print(f"Remix ID: {self.id}")

        #self.title = json_data["projectname"]

        #self.description = json_data["description"] if "description" in json_data else None
        #self.instructions = json_data["instructions"] if "instructions" in json_data else None

        #self.visible = json_data["visibility"] == "visible"
        #self.public = json_data["public"]
        #self.comments_allowed = json_data["comments_allowed"]
        #self.is_published = json_data["is_published"]
        #self.project_token = json_data["project_token"]


class RemixtreeProject:

    def __init__(self, data):
        self.id = data["id"]
        self.author = data["username"]
        self.moderation_status = data["moderation_status"]
        self.title = data["title"]

        self.created_timestamp = data["datetime_created"]["$date"]
        self.last_modified_timestamp = data["mtime"]["$date"]
        self.shared_timestamp = (
            data["datetime_shared"]["$date"] if data["datetime_shared"] else None
        )


class ScratchSession:

    def __init__(self, username=None):
        self.logged_in = False
        self.username = username
        self.csrf_token = None
        
        self.proxies = {
      
            'http': 'socks5h://tor_proxy:9050',
            'https': 'socks5h://tor_proxy:9050'

        }
        
    def get_project(self, project):
        print("donde")
        print("PROJECT", project)
        project_id = (project.id if isinstance(project, (RemixtreeProject, Project)) else project)
        print("donde")
        params = {
            ':username': project['username'],
            ':projectname': project['projectname'],  # Busca por nombre de proyecto
      
        }
        session = requests.Session()

        prepared_request = session.prepare_request(requests.Request('GET', consts.URL_SNAP_API, params=params))


        print(prepared_request.url)
        #url = f'{consts.URL_SNAP_API}/{project.get("username")}/{project.get("projectname")}'
        #print(url)
        #print("Esto es ", requests.get(consts.URL_SNAP_API, params=params, proxies=self.proxies))
        
        #response = requests.get(f'{consts.URL_SNAP_API}/metadata', params=params, proxies=self.proxies)   
        #url = f'{consts.URL_SNAP_API}/:{project.get("username")}/:{project.get("projectname")}/metadata'  
        #url = f'{consts.URL_SNAP_API}/{project.get("username")}/{project.get("projectname")}/metadata'  
        url = f'{consts.URL_SNAP_API}/{project.get("username")}/{project.get("projectname")}'        
      
      
        print(url)
        response = requests.get(url, proxies=self.proxies)
        print("solicitud", response)  
 
        if response.status_code == 200:

            if 'application/json' in response.headers['Content-Type']:
                print("La respuesta  es un JSON válido")
                html_content = response.json()

                print(html_content)

            else:

                print("La respuesta no es un JSON válido")

                #print(response.content)
        return response.text
            #print(f"Project Name: {response.id}")
            #requests.get(consts.URL_SNAP_API, params=params, proxies=self.proxies).json()
            #requests.get(f'{consts.URL_SNAP_API}/{project.get("projectname")}', proxies=self.proxies).json()
        

   