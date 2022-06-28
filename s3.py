import boto3
import os
from pathlib import Path
import glob
import funcs as f
import re
import aioboto3
import asyncio
import concurrent.futures
import functools

class S3():
    # static_key_id = f.get_val_in_local_storage('static_key_id')
    # static_secret_key = f.get_val_in_local_storage('static_secret_key')

    # client = boto3.client(
    #     's3',
    #     # aws_access_key_id = static_key_id,
    #     # aws_secret_access_key = static_secret_key,
    #     aws_access_key_id = static_key_id,
    #     aws_secret_access_key = static_secret_key,
    #     region_name = 'ru-central1',
    #     endpoint_url = 'https://storage.yandexcloud.net'
    # )

    def __init__(self):
        super(S3, self).__init__()
        #self.load_static_key()
        self.client()

    def client(self):
        static_key_id = f.get_val_in_local_storage('static_key_id')
        static_secret_key = f.get_val_in_local_storage('static_secret_key')
        client = boto3.client(
            's3',
            aws_access_key_id=static_key_id,
            aws_secret_access_key=static_secret_key,
            region_name='ru-central1',
            endpoint_url='https://storage.yandexcloud.net'
        )
        return client

    def resource(self):
        static_key_id = f.get_val_in_local_storage('static_key_id')
        static_secret_key = f.get_val_in_local_storage('static_secret_key')
        resource = boto3.resource(
            's3',
            aws_access_key_id=static_key_id,
            aws_secret_access_key=static_secret_key,
            region_name='ru-central1',
            endpoint_url='https://storage.yandexcloud.net'
        )
        return resource

    def upload_dir(localDir, awsInitDir, bucketName, tag, prefix):
        client = S3.client(None)
        """
        from current working directory, upload a 'localDir' with all its subcontents (files and subdirectories...)
        to a aws bucket
        Parameters
        ----------
        localDir :   localDirectory to be uploaded, with respect to current working directory
        awsInitDir : prefix 'directory' in aws
        bucketName : bucket in aws
        tag :        tag to select files, like *png
                     NOTE: if you use tag it must be given like --tag '*txt', in some quotation marks... for argparse
        prefix :     to remove initial '/' from file names

        Returns
        -------
        None
        """
        cwd = str(Path.cwd())
        p = Path(os.path.join(Path.cwd(), localDir))
        mydirs = list(p.glob('**'))
        for mydir in mydirs:
            fileNames = glob.glob(os.path.join(mydir, tag))
            fileNames = [f for f in fileNames if not Path(f).is_dir()]
            rows = len(fileNames)
            for i, fileName in enumerate(fileNames):
                fileName = str(fileName).replace(cwd, '')
                if fileName.startswith(prefix):  # only modify the text if it starts with the prefix
                    fileName = fileName.replace(prefix, "", 1) # remove one instance of prefix
                print(f"fileName {fileName}")

                awsPath = os.path.join(awsInitDir, str(fileName))

                client.upload_file(fileName, bucketName, awsPath)

    def get_object_list(bucket_name,directory,delimiter):
        client = S3.client(None)
        objects = client.list_objects(Bucket=bucket_name, Prefix=directory, Delimiter=delimiter)['Contents']
        #print(objects)
        return objects

    def download_s3_folder(bucket_name, s3_folder, local_dir=None):
        resource = S3.resource(None)
        bucket = resource.Bucket(bucket_name)
        for obj in bucket.objects.filter(Prefix=s3_folder):
            target = local_dir+obj.key
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            if obj.key[-1] == '/':
                continue
            bucket.download_file(obj.key, target)

    def download(bucket_name,objects,single=None):
        client = S3.client(None)
        local_path = f.get_val_in_local_storage('local_path')
        #print(objects)
        for item in objects:
            if '/' in item:
                S3.download_s3_folder('ist-pnipu-bucket', item,local_path)
            else:
                cloud_object_name = str(item).split('/')
                formated_obj_name = cloud_object_name[len(cloud_object_name)-1]
                print('это из s3 '+local_path+formated_obj_name)
                client.download_file(bucket_name, item, local_path+formated_obj_name)

    def put(self,bucket_name,object):
        client = S3.client(None)
        client.put_object(Bucket=bucket_name, Key=object)

    def upload(self,bucket_name,objects,curr_path):
        client = S3.client(None)
        for obj in objects:
            formated_local_path = (obj)[3:]
            formated_local_path = str(formated_local_path).split('/')
            file_without_path = formated_local_path[-1]
            #print(file_without_path)
            #del path_wihtout_disk_flag[-1]

            new_path = ''
            # for key in path_wihtout_disk_flag:
            #     new_path += key+'/'
            #     #print(new_path)
            #
            #     #client.put_object(Bucket=bucket_name, Key=new_path)
            client.upload_file(obj, bucket_name, curr_path+file_without_path)
            #print(new_path)

    def delete(bucket_name, objects, current_path):
        client = S3.client(None)
        for obj in objects:
            print(current_path + obj)
            client.delete_object(Bucket=bucket_name, Key=current_path + obj)

    def uploadDirectory(path, bucketname):
        client = S3.client(None)
        for root, dirs, files in os.walk(path):
            for file in files:
                client.upload_file(os.path.join(root, file), bucketname, file)

    def upload_folder_to_s3(s3bucket, inputDir, s3Path):
        client = S3.client(None)
        print("Uploading results to s3 initiated...")
        print("Local Source:", inputDir)
        os.system("ls -ltR " + inputDir)

        print("Dest  S3path:", s3Path)

        try:
            for path, subdirs, files in os.walk(inputDir):
                for file in files:
                    dest_path = path.replace(inputDir, "")
                    __s3file = os.path.normpath(s3Path + '/' + dest_path + '/' + file)
                    __local_file = os.path.join(path, file)
                    print("upload : ", __local_file, " to Target: ", __s3file, end="")
                    client.upload_file(__local_file, s3bucket, __s3file)
                    print(" ...Success")
        except Exception as e:
            print(" ... Failed!! Quitting Upload!!")
            print(e)
            raise e

    #upload_folder_to_s3("ist-pnipu-bucket", "E:/torrent/content/Thinstall", "2022/")
    #upload_dir('E:/temp/emu8086','2022/','ist-pnipu-bucket','*','')
    #uploadDirectory('E:/torrent/content/Thinstall','ist-pnipu-bucket')

    # loop = asyncio.get_event_loop()
    # data = loop.run_until_complete(get_object_list('ist-pnipu-bucket', '', ''))
    # loop.close() # I had to skip this line, though I expect that was an issue with jupyter maybe.
