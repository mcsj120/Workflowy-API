from workflowy.workflowy_transport import WorkFlowyTransport
from workflowy.workflowy_exception import WorkFlowyException
import re
import random
import requests

class WorkFlowyList:
    """
    Represents a list in WorkFlowy.

    Attributes:
    - id: The unique identifier of the list (string).
    - name: The name of the list (string).
    - description: The description of the list (string).
    - level: The level of the list in the hierarchy (integer).
    - creation_time: The timestamp of when the list was created (integer).
    - last_modified_time: The timestamp of when the list was last modified (integer).
    - completed_time: The timestamp of when the list was completed (integer).
    - sublists: The sublists contained within the list (list of WorkFlowyList objects).
    - main_list: The main list to which the list belongs (WorkFlowyProject object).
    - transport: The transport object used for making API requests (WorkFlowyTransport object).
    """

    def __init__(
        self,
        id,
        name,
        description,
        level,
        creation_time,
        last_modified_time,
        completed_time,
        sublists,
        main_list,
        transport,
        metadata=None
    ):
        """
        Initializes a WorkFlowyList object.

        Parameters:
        - id: The unique identifier of the list (string).
        - name: The name of the list (string).
        - description: The description of the list (string).
        - level: The level of the list in the hierarchy (integer).
        - creation_time: The timestamp of when the list was created (integer).
        - last_modified_time: The timestamp of when the list was last modified (integer).
        - completed_time: The timestamp of when the list was completed (integer).
        - sublists: The sublists contained within the list (list of WorkFlowyList objects).
        - main_list: The main list to which the list belongs (WorkFlowyProject object).
        - transport: The transport object used for making API requests (WorkFlowyTransport object).
        - metadata: Optional metadata dict containing extra node properties.
        """
        self.id = id if isinstance(id, str) else ''
        self.name = name if isinstance(name, str) else ''
        self.description = description if isinstance(description, str) else ''
        self.level = level if isinstance(level, int) else -1
        self.creation_time = creation_time if isinstance(creation_time, int) else 0
        self.last_modified_time = last_modified_time if isinstance(last_modified_time, int) else 0
        self.completed_time = completed_time if isinstance(completed_time, int) else 0
        self.sublists = []
        self.metadata = metadata if isinstance(metadata, dict) else {}

        # Check sublists
        if isinstance(sublists, list):
            for sublist in sublists:
                if isinstance(sublist, WorkFlowyList):
                    self.sublists.append(sublist)
                else:
                    raise WorkFlowyException('Sublists must be a WorkFlowyList object')

        # Check list
        if main_list.__class__.__name__ == 'WorkFlowyProject':
            self.main_list = main_list
        else:
            raise WorkFlowyException('List must be a WorkFlowyProject object')
        
        # Check transport
        if isinstance(transport, WorkFlowyTransport):
            self.transport = transport
        else:
            raise WorkFlowyException('Transport must be a WorkFlowyTransport object')
        

    def search_sublist(self, expression: str, get_all: bool = False, exact_match: bool = False) -> list:
        """
        Search for a sublist by name using regular expression.

        Args:
            expression (str): The search expression to match against sublist names.
            get_all (bool, optional): If True, returns all sublists with matching names. 
                                      If False, returns the first sublist with a matching name. 
                                      Defaults to False.
            exact_match (bool, optional): If True, performs an exact match against sublist names. 
                                          If False, performs a case-insensitive search using regular expression. 
                                          Defaults to False.

        Returns:
            list: A list of matching sublists. If no matches are found, returns an empty list.
        """
        
        # Check name
        if not isinstance(expression, str):
            raise WorkFlowyException('Search expression must be a string')
        
        matches = []
        if (exact_match and expression == self.name) or (not exact_match and re.search(expression, self.name, re.IGNORECASE)):
            matches.append(self)
            if not get_all:
                return matches
            
        for sublist in self.sublists:
            match = sublist.search_sublist(expression, get_all, exact_match)
            if match:
                matches.extend(match)
                if not get_all and len(matches) > 0:
                    return matches
            
        return matches if matches else False


    def get_id(self):
        """
        Get the unique identifier of the list.

        Returns:
            str: The unique identifier of the list.
        """
        return self.id
    

    def get_name(self):
        """
        Get the name of the list.

        Returns:
            str: The name of the list.
        """
        return self.name
    

    def get_description(self):
        """
        Get the description of the list.

        Returns:
            str: The description of the list.
        """
        return self.description
    

    def get_creation_time(self):
        """
        Get the timestamp of when the list was created.

        Returns:
            int: The timestamp of when the list was created.
        """
        return self.creation_time
    

    def get_last_modified_time(self):
        """
        Get the timestamp of when the list was last modified.

        Returns:
            int: The timestamp of when the list was last modified.
        """
        return self.last_modified_time
    

    def get_completed_time(self):
        """
        Get the timestamp of when the list was completed.

        Returns:
            int: The timestamp of when the list was completed.
        """
        return self.completed_time
    

    def get_parent(self):
        """
        Get the parent list of the current list.

        Returns:
            WorkFlowyList: The parent list of the current list.
        """
        return self.main_list.get_list_parent(self.id)


    def is_completed(self):
        """
        Check if the list is completed.

        Returns:
            bool: True if the list is completed, False otherwise.
        """
        return self.completed_time != 0
    

    def get_level(self):
        """
        Get the level of the list in the hierarchy.

        Returns:
            int: The level of the list in the hierarchy.
        """
        return self.level
    
    # TODO: Implement getting OPML of the list 
    def get_opml(self):
        """
        Get the OPML representation of the list.

        Returns:
            str: The OPML representation of the list.
        """
        pass


    def get_sublists(self):
        """
        Get the sublists contained within the list.

        Returns:
            list: A list of WorkFlowyList objects representing the sublists.
        """
        return self.sublists


    def get_metadata(self):
        """
        Get the metadata of the list/node.

        Returns:
            dict: The metadata dictionary of the list/node.
        """
        return self.metadata


    def is_file(self) -> bool:
        """
        Check if the list/node represents a file attachment.

        Returns:
            bool: True if the list/node is a file attachment, False otherwise.
        """
        return "s3File" in self.metadata


    def get_file_info(self) -> dict:
        """
        Get the S3 file information if the list/node represents a file.

        Returns:
            dict: A dictionary with keys like 'isFile', 'fileName', 'fileType', 'objectFolder', etc.
                  Returns an empty dictionary if it's not a file.
        """
        return self.metadata.get("s3File", {})




    def get_signed_file_url(self, resolution: str = "800x800") -> str:
        """
        Request and retrieve a temporary signed download URL for the file/image.

        Args:
            resolution (str, optional): The resolution for image files. Defaults to "800x800".

        Returns:
            str: The signed download URL, or None if it is not a file or has no objectFolder.
        """
        if not self.is_file():
            return None

        file_info = self.get_file_info()
        object_folder = file_info.get("objectFolder")
        if not object_folder:
            return None

        user_id = getattr(self.main_list, "user_id", None)
        if not user_id:
            try:
                # Try to retrieve user_id from initialization data
                init_data = self.transport.get_initialization_data()
                user_id = init_data.get("user", {}).get("id")
                self.main_list.user_id = user_id
            except Exception:
                return None

        from urllib.parse import quote
        encoded_folder = quote(object_folder)
        signed_preview_url = f"https://workflowy.com/file-proxy/signed-preview/{user_id}/{self.id}/{resolution}/?attempt=1&folder={encoded_folder}"

        try:
            headers = {
                "Cookie": f"sessionid={self.transport.session_id}",
                "Referer": "https://workflowy.com/"
            }
            res = self.transport.session.get(signed_preview_url, headers=headers, timeout=15)
            res.raise_for_status()
            return res.json().get("url")
        except Exception:
            return None


    def download_file(self, destination_path: str, resolution: str = "800x800") -> bool:
        """
        Download the file/image to the specified local destination path.

        Args:
            destination_path (str): The local file path to save the downloaded file.
            resolution (str, optional): The resolution for image files. Defaults to "800x800".

        Returns:
            bool: True if the download was successful, False otherwise.
        """
        download_url = self.get_signed_file_url(resolution=resolution)
        if not download_url:
            return False

        try:
            res = requests.get(download_url, stream=True, timeout=20)
            res.raise_for_status()
            with open(destination_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception:
            return False
    

    def get_list(self, id: str):
        """
        Get the list with the given ID.

        Args:
            id (str): The ID of the list to retrieve.

        Returns:
            WorkFlowyList: The list with the given ID.

        Raises:
            WorkFlowyException: If the list with the given ID is not found.
        """
        if id in self.main_list.all_lists.items():
            return self.main_list.all_lists[id]
        else:
            raise WorkFlowyException(f"List {id} not found")
        
    def get_list_by_name(self, name: str):
        """
        Get the list with the given name.

        Args:
            name (str): The name of the list to retrieve.

        Returns:
            WorkFlowyList: The list with the given name.

        Raises:
            WorkFlowyException: If the list with the given name is not found.
        """
        for id, workflowy_list in self.main_list.all_lists.items():
            if workflowy_list.get_name() == name:
                return self.main_list.all_lists[id]
        raise WorkFlowyException(f"List {id} not found")
    
    def get_list_by_name_nested(self, names: list[str]):
        """
        Get the list with the given name.

        Args:
            names (list[str]): A list of the names of nodes.

        Returns:
            WorkFlowyList: The list with the given name of the last item in the input list.

        Raises:
            WorkFlowyException: If the list with the given path is not found.
        """
        current_list = self.main_list
        found = False
        for index, name in enumerate(names):
            for id, workflowy_list in current_list.all_lists.items():
                if workflowy_list.get_name() == name:
                    if index == len(names) - 1:
                        return current_list.all_lists[id]
                    else:
                        found = True
                        current_list = current_list.all_lists[id].main_list
                        break
            if not found:
                 raise WorkFlowyException(f"List {id} not found")
            found = False
        raise WorkFlowyException(f"List {id} not found")
        

    # Setters

    def set_name(self, name: str):
        """
        Set the name of the list.

        Args:
            name (str): The new name of the list.
        """
        self.name = name
        self.transport.listRequest('edit', {
            'projectid': self.id,
            'name': name
        })
        
    
    def set_description(self, description: str):
        """
        Set the description of the list.

        Args:
            description (str): The new description of the list.
        """
        self.description = description
        self.transport.listRequest('edit', {
            'projectid': self.id,
            'description': description
        })

    def set_any(self, undo_data=None, **kwargs):
        """
        Set the any of the list.

        Args:
            kwargs: A dictionary of key-value pairs to set.
        """
        request_obj = {
            'projectid': self.id,
            **kwargs
        }
        if undo_data is not None:
            request_obj['undo_data'] = undo_data
        self.transport.listRequest('edit', request_obj)


        

    def set_complete(self, complete: bool):
        """
        Set the completion status of the list.

        Args:
            complete (bool): True to mark the list as completed, False to mark it as incomplete.
        """
        if complete:
            self.transport.listRequest('complete', {
                'projectid': self.id
            })
        else:
            self.transport.listRequest('uncomplete', {
                'projectid': self.id
            })
            self.completed_time = 0


    def move(self, destination, priority: int = 0):
        """
        Move the list to a new destination.

        Args:
            destination (WorkFlowyList): The new destination list.
            priority (int, optional): The priority of the list in the new destination. Defaults to 0.

        Raises:
            WorkFlowyException: If the destination is not a WorkFlowyList object, is the same as self, or is the root.
        """
        if not isinstance(destination, self.__class__):
            raise WorkFlowyException('Destination must be a WorkFlowyList object')
        
        # Check that the destination is not self
        if destination.id == self.id:
            raise WorkFlowyException('Destination cannot be self')
        
        # Check that the destination is not root
        if destination.level == 0:
            raise WorkFlowyException('Moving to root is not currently supported')
        
        source_parent = self.get_parent()
        # Check that the destination is not a child of self. Break if the destination is the root.
        parent = destination.get_parent()
        while self.level < parent.level:
            if parent.id == self.id:
                raise WorkFlowyException('Destination cannot be a child of self')
            parent = parent.get_parent()
            # Break if the parent is the root
            if not parent:
                break
        
        self.transport.listRequest('move', {
            'projectid': self.id,
            'parentid': destination.id,
            'priority': priority
        })

        # Update the levels
        self.__update_levels(destination.level + 1)
        
        
        # Update the main list
        self.main_list.all_lists[self.id] = self
        # Update the parent_ids
        self.main_list.parent_ids[self.id] = destination.get_id()

        # Update the sublists
        source_parent.sublists.remove(self)
        destination.sublists.insert(priority, self)


    def delete(self):
        """
        Delete the list.

        Raises:
            WorkFlowyException: If the list is the root.
        """
        if self.level == 0:
            raise WorkFlowyException('Deleting the root is not currently supported')

        self.transport.listRequest('delete', {
            'projectid': self.id
        })
        self.get_parent().sublists.remove(self)
        self.main_list.all_lists.pop(self.id)
        self.main_list.parent_ids.pop(self.id)


    def create_sublist(
        self, name: str = None, description: str = None, priority: int = 0, metadata: dict = {}
    ) -> 'WorkFlowyList':
        """
        Create a new sublist within the current list.

        Args:
            name (str, optional): The name of the new sublist. Defaults to None.
            description (str, optional): The description of the new sublist. Defaults to None.
            priority (int, optional): The priority of the new sublist. Defaults to 0.
        """
        new_id = self.__generate_id()

        self.transport.listRequest('create', {
            'projectid': new_id,
            'parentid': self.id,
            'priority': priority,
        })

        properties = {}

        if name:
            properties['name'] = name
        if description:
            properties['description'] = description
        if metadata:
            properties['metadataPatches'] = [metadata]
        
        if properties: # Only send the request if there are properties to set
            self.transport.listRequest('edit', {
                'projectid': new_id,
                **properties # Merge the properties into the request
            })
    
        # Update the main list
        new_list = WorkFlowyList(
            id=new_id,
            name=name,
            description=description,
            level=self.level + 1,
            creation_time=0,
            last_modified_time=0,
            completed_time=0,
            sublists=[],
            main_list=self.main_list,
            transport=self.transport
        )
        self.main_list.all_lists[new_id] = new_list
        self.main_list.parent_ids[new_id] = self.id
        self.sublists.insert(priority, new_list)
        return new_list


    def __generate_id(self):
        """
        Generate a unique identifier for the list.

        Returns:
            str: The generated unique identifier.
        """
        id_parts = []
        for _ in range(2):
            id_part = format(int((1 + random.random()) * 65536) | 0, 'x')[1:]
            id_parts.append(id_part)
        id_parts.append('-')

        for _ in range(3):
            id_part = format(int((1 + random.random()) * 65536) | 0, 'x')[1:]
            id_parts.append(id_part)
            id_parts.append('-')

        for _ in range(3):
            id_part = format(int((1 + random.random()) * 65536) | 0, 'x')[1:]
            id_parts.append(id_part)

        return ''.join(id_parts)


    def __update_levels(self, level: int):
        """
        Update levels for self and all its sublists recursively.

        Args:
            level (int): The new level to set for the list and its sublists.
        """
        self.level = level
        for sublist in self.sublists:
            sublist.__update_levels(level + 1)