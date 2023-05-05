from base import ClientGeneric


# @for_all_methods(['__init__'], debuglog())
class ClientPowerSchool(ClientGeneric):
    """
    It takes a list of lists, and returns a list of lists, where each list is a list of the unique elements of the original
    lists
    :return: A list of dictionaries.
    """

    def full_list(self):
        """
        It returns a list of all the elements in the tree.
        """
        full_list = self.get('fileList',[])
        full_list.extend(self.get('byYearList',[]))
        full_list.extend(self.get('streamList',[]))
        return full_list

