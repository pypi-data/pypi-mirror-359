import re
from pathlib import Path
from pysftp import Connection
from paramiko import SFTPClient


def seq_rename(new_directory: str | Path, current_file_name: str, file_extension: str) -> str:
    """Checks the new directory for documents with the same name. If there is a document with 
    the same name, it will return with a new document name with (#) at the end of it. EG: test (1).csv

    Args:
        new_directory (str | Path): The direcotry you want to copy the document to.
        current_file_name (str): The name of the current document. 
        file_extension (str): The extension of the current doc in the form '.extension'. EG: '.pdf'

    Returns:
        str: Returns the name of the name of the document to be used. If a document with that name 
        does not exist, it will retain the same name. Otherwise it will have a (#) at the end of the name.
    """
    
    search_param = re.compile(r'(\(\d+\))')
    regex_search = re.search(search_param, current_file_name)
    if Path(new_directory).joinpath(f'{current_file_name}{file_extension}').exists():
        if regex_search:
            file_num = re.sub('[()]', '', regex_search.group(0))
            file_name_no_num = re.sub(
                search_param, '', current_file_name).strip()
            new_num = int(file_num) + 1
            new_file_name = f'{file_name_no_num} ({new_num})'
        else:
            new_file_name = f'{current_file_name} (1)'
    else:
        return f'{current_file_name}'

    if Path(new_directory).joinpath(f'{new_file_name}{file_extension}').exists():
        return seq_rename(new_directory, new_file_name, file_extension)
    else:
        return f'{new_file_name}'


def pysftp_seq_rename(ftp_session: Connection, new_directory: str | Path,
                      current_file_name: str, file_extension: str) -> str:
    """Uses your pyfstp connection and checks the directory you wish to copy your document into for 
    documents with the same name. If there is a document with the same name, it will return with a 
    new document name with (#) at the end of it. EG: test (1).csv

    Args:
        ftp_session (Connection): Your pysftp connection.
        new_directory (str | Path): The direcotry you want to copy the document to.
        current_file_name (str): The name of the current document.
        file_extension (str): The extension of the current doc in the form '.extension'. EG: '.pdf'

    Returns:
        str: Returns the name of the name of the document to be used. If a document with that name 
        does not exist, it will retain the same name. Otherwise it will have a (#) at the end of the name.
    """
    
    search_param = re.compile(r'(\(\d+\))')
    regex_search = re.search(search_param, current_file_name)
    if ftp_session.exists(f'{new_directory}/{current_file_name}{file_extension}'):
        if regex_search:
            file_num = re.sub('[()]', '', regex_search.group(0))
            file_name_no_num = re.sub(
                search_param, '', current_file_name).strip()
            new_num = int(file_num) + 1
            new_file_name = f'{file_name_no_num} ({new_num})'
        else:
            new_file_name = f'{current_file_name} (1)'
    else:
        return f'{current_file_name}'

    if ftp_session.exists(f'{new_directory}/{new_file_name}{file_extension}'):
        return seq_rename(new_directory, new_file_name, file_extension)
    else:
        return f'{new_file_name}'


def paramiko_seq_rename(sftp_session: SFTPClient, destination: str, current_file_name: str, 
                        file_extension: str) -> str:
    """Uses your paramiko connection and checks the directory you wish to copy your document into for 
    documents with the same name. If there is a document with the same name, it will return with a 
    new document name with (#) at the end of it. EG: test (1).csv

    Args:
        sftp_session (SFTPClient): Your paramiko connection. 
        destination (str): The direcotry you want to copy the document to.
        current_file_name (str): The name of the current document.
        file_extension (str): The extension of the current doc in the form '.extension'. EG: '.pdf'

    Returns:
        str: Returns the name of the name of the document to be used. If a document with that name 
        does not exist, it will retain the same name. Otherwise it will have a (#) at the end of the name.
    """
    
    search_param = re.compile(r'(\(\d+\))')
    regex_search = re.search(search_param, current_file_name)
    try:
        sftp_session.stat(f'{destination}/{current_file_name}{file_extension}')
        if regex_search:
            file_num = re.sub('[()]', '', regex_search.group(0))
            file_name_no_num = re.sub(
                search_param, '', current_file_name).strip()
            new_num = int(file_num) + 1
            new_file_name = f'{file_name_no_num} ({new_num})'
        else:
            new_file_name = f'{current_file_name} (1)'
    except FileNotFoundError:
        return f'{current_file_name}'
    
    try:
        sftp_session.stat(f'{destination}{new_file_name}{file_extension}')
        return paramiko_seq_rename(sftp_session, destination, new_file_name, file_extension)
    except FileNotFoundError:
        return f'{new_file_name}'