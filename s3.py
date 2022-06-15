import boto3
import os
from pathlib import Path
import glob
import funcs as f

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

    def download(bucket_name,objects,object_name):
        client = S3.client(None)
        for object_path in objects:
            local_path = f.get_val_in_local_storage('local_path')+object_path
            local_path_without_obj_name = local_path.replace(object_name,'')
            print(local_path_without_obj_name)
            # если папки не существует
            if not os.path.exists(local_path_without_obj_name):
                os.makedirs(local_path_without_obj_name)
                client.download_file(bucket_name, object_path, local_path)
            else:
                # если файла не существует
                if not os.path.isfile(local_path):
                    client.download_file(bucket_name, object_path, local_path)
                else:
                    print('файл '+object_path+ ' существует')

    def upload(self,bucket_name,objects):
        client = S3.client(None)
        for obj in objects:
            format_path = (obj)[3:]
            format_path = str(format_path).split('/')
            filename = format_path[-1]
            del format_path[-1]
            new_path = ''
            for key in format_path:
                new_path += key+'/'
                #print(new_path)

                client.put_object(Bucket=bucket_name, Key=new_path)
            client.upload_file(obj, bucket_name, new_path+filename)
            #print(new_path)

    def delete(bucket_name,objects,current_path):
        client = S3.client(None)
        for obj in objects:
            print(current_path+obj)
            client.delete_object(Bucket=bucket_name, Key=current_path+obj)

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


