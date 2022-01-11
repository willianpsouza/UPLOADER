

import os
import uuid
from flask import Flask, flash, request, redirect, url_for,Response,send_file
from werkzeug.utils import secure_filename
from json import dumps

'''
Basico para o ambiente:
    apt install python3-venv
    apt install python3-pip

Criando um virtual environment:
    python3 -m venv UPLOADER
    source UPLOADER/bin/activate
    #instalando basico:
    pip3 install flask uwsgi requests
    #saindo

Abra uma janela e teste com curl ! ou faca uma pagina html ai e com vc

CURL EXAMPLE:
    curl -X POST  -F 'username=willian' -F 'password=jose' http://127.0.0.1:5000                                        #-- Criando Hash, auth_key  

    curl -X POST  -F 'auth_key=975edecd1d3f5b9d20649c44ca6b5bc7' http://127.0.0.1:5000                                  #-- Listando arquivos do usuario da auth_key
    curl -X POST -F 'file=@./NetBSD-9.2-amd64.iso' -F 'auth_key=975edecd1d3f5b9d20649c44ca6b5bc7' http://127.0.0.1:5000 #-- Postando um arquivo

    curl -X POST  -F 'uuid=ef31fa1f-fb2b-4d99-b049-b2722a11076c' --output jose.iso http://127.0.0.1:5000                                  #-- Recuperando o arquivo
    checando arquivo:
    md5sum jose.iso             35cef6acb18dfda014710f3cb8520794  jose.iso
    md5sum NetBSD-9.2-amd64.iso 35cef6acb18dfda014710f3cb8520794  NetBSD-9.2-amd64.iso


    curl -X POST -F 'erase=yes' -F 'uuid=ef31fa1f-fb2b-4d99-b049-b2722a11076c' http://127.0.0.1:5000                                  #-- Apagando o arquivo

'''

UPLOAD_FOLDER = '/path/to/the/uploads'
UPLOAD_FOLDER = '/home/willian_pires/Programas/python3/UPLOADER/UPDATA'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp3','mp4','iso'}
FILE_SIZE = 512  #512MB para testes locais

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = FILE_SIZE * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def search_files(search,tp='auth_key'):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(UPLOAD_FOLDER):
        for file in f:
            (auth_key,suuid,size,filename) = file.split('^')
            if tp == 'auth_key' and search == auth_key:
                files.append(file)
            elif tp == 'uuid' and search == suuid:
                files.append(file)
    return files

@app.route('/', methods=['GET', 'POST'])
def main():
    ret = { 'status' : 'Start'}
    search_uuid,auth_key = None,None

    if request.method == 'POST':
        if 'username' in request.form.keys() and 'password' in request.form.keys():
            import hashlib
            string_key = '%s:%s' % (request.form['username'],request.form['password'])
            ret['auth_key'] = hashlib.md5(bytes(string_key,'UTF-8')).hexdigest()
            return Response(dumps(ret),mimetype='application/javascript')

        if 'uuid' in request.form.keys():
            if len(request.form['uuid']) == 36:
                search_uuid = request.form['uuid']
    
        if  'auth_key' in request.form.keys():
            if len(request.form['auth_key']) == 32:
                auth_key = request.form['auth_key']

        if  'uuid' in request.form.keys() and 'erase' in request.form.keys():
            files = search_files(search_uuid,'uuid')
            if len(files) == 1:
                os.unlink(os.path.join(app.config['UPLOAD_FOLDER'],files[0]))
                ret['status'] = 'DELETED'
                ret['file'] = files[0]
                return Response(dumps(ret),mimetype='application/javascript')

        if 'file' not in request.files:
            if auth_key:
                files = search_files(auth_key)

            if search_uuid:
                files = search_files(search_uuid,'uuid')
                if len(files) == 1:
                    return send_file(os.path.join(app.config['UPLOAD_FOLDER'],files[0]),attachment_filename=files[0].split('^')[3])
            return Response(dumps(files),mimetype='application/javascript')
        else:
            file = request.files['file']
            if file.filename.strip() == '':
                return Response(dumps(ret),mimetype='application/javascript')

            if file and allowed_file(file.filename):
                suuid = str(uuid.uuid4())
                filesize = request.content_length
                filename = '%s^%s^%s^%s' % (auth_key, suuid,filesize,secure_filename(file.filename))
                #
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                os.chmod(os.path.join(app.config['UPLOAD_FOLDER'], filename),0o600)
                ret['status'] = 'OK'
                ret['filename'] = filename
                ret['filesize'] = filesize
                ret['auth_key'] = auth_key
                ret['uuid'] = suuid
            return Response(dumps(ret),mimetype='application/javascript')
    return Response(dumps({}),mimetype='application/javascript')

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
