from __future__ import with_statement
import logging
from fabric.api import *
import json,sys,os

from contextlib import contextmanager
from fabric.api import prefix
from contextlib import contextmanager as _contextmanager

env.debug = True

@_contextmanager
def virtualenv(user_acc,venv_name):
    with cd('/home/%s/.virtualenvs/%s'%(user_acc,venv_name)):
        with prefix('source /home/%s/.virtualenvs/%s/bin/activate'%(user_acc,venv_name)):
            yield
def su(pwd,user,command):
    with settings(
         password="%s"%pwd,
         sudo_prefix="su %s -c " %user,
         sudo_prompt="Password:"
         ):
         sudo(command)
def deployapp(cfg_file='cfg.json',server="DEVSERVER1"):
    try:
        tmp_cfg = open(cfg_file).read()
        cfg = json.loads(tmp_cfg)
        env.user = cfg[server]["python_app"]["user_acc"]
        user_acc = env.user
        env.password = cfg[server]["python_app"]["user_pass"]
        user_pass = env.password
        base_dir = cfg[server]["python_app"]["base_dir"]
        tools_dir = base_dir + 'PythonApp/hpro/tools/'
        conf_dir = base_dir + 'PythonApp/hpro/conf/'
        manager_dir = base_dir + 'PythonApp/hpro/manager/'
        settings_dir = base_dir + 'PythonApp/hpro/hpro/'

        print cfg

        target = open('myAppConf.py','w')
        target.write("APP_CONFIG = ")
        target.write(str(cfg[server]["python_app"]["APP_CONFIG"]))
        target.write("\n")
        target.close()
        target = open('default_db_config.py','w')
        target.write("DATABASES = ")
        target.write(str(cfg[server]["python_app"]["DATABASES"]))
        target.write("\n")
        target.close()
        with settings(host_string=cfg[server]["python_app"]["APP_CONFIG"]["MY_ADDR"],warn_only =True):
            with cd(base_dir):
                r = run("mv PythonApp PythonApp-BefUpgrade")
                r = run("git clone %s"%cfg[server]["python_app"]["repo_url"])
            if r.failed:
                print("Could not clone the repo!!")
            else:
                put('myAppConf.py',conf_dir)
                put('default_db_config.py',tools_dir)
                with virtualenv(user_acc,cfg[server]["python_app"]["VIRTUAL_ENV_NAME"]):
                    run('pip install -r /home/%s/PythonApp/requirements.txt'%(user_acc)) 
                    with cd(base_dir):
                        execute(su, user_pass, user_acc,   
                                'python %sPythonApp/hpro/tools/db_config_builder.py -u%s -p%s -D%sPythonApp/hpro/tools/' 
                                 %(base_dir,
                                   cfg[server]["python_app"]["DATABASES"]["default"]["USER"],
                                   cfg[server]["python_app"]["DATABASES"]["default"]["PASSWORD"],
                                   base_dir
                                   ))
                    r = run('cat /home/%s/databases_config.py '%(user_acc))
                    r = run('cat /home/%s/app2db.py '%(user_acc))
                    r = run('mv /home/%s/databases_config.py %s'%(user_acc,settings_dir))
                    if r.failed:
                        print("Could not mv databases_config!!")
                    r = run('mv /home/%s/app2db.py %s'%(user_acc,manager_dir))
                    if r.failed:
                        print("Could not mv app2db.py !!")
                    with cd(base_dir+"PythonApp"):
                        execute(su, user_pass, user_acc, 'python -m compileall .')
                        execute(su, user_pass, user_acc, 'supervisorctl restart all')
                    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print( "Exception (%s:%s): %s" %(fname,exc_tb.tb_lineno,str(e)))

def setup(cfg_file = 'cfg.json',server="DEVSERVER1",fresh_deployment=False):
    try:
        tmp_cfg = open(cfg_file).read()
        cfg = json.loads(tmp_cfg)
        print cfg
        with settings(warn_only=True):
            print ("Trying to run task on %s for user (%s) with pass(%s)"%(env.hosts,env.user,env.password))
            env.user = "naveena"
            env.password = "naveena"
            user_acc = cfg[server]["python_app"]["user_acc"]
            user_pass = cfg[server]["python_app"]["user_pass"]
            base_dir = cfg[server]["python_app"]["base_dir"]
            if 'True' == fresh_deployment:
                print ("Fresh Deploymet")
                result = sudo("useradd -d /home/%s/ -G www-data,sudo -m -s /bin/bash %s"%(user_acc,user_acc))
                result = sudo("echo '%s\n%s\n' > p.txt "%(user_pass,user_pass))
                result = sudo("passwd %s < p.txt"%user_acc)
                result = sudo("apt-get install nginx supervisor")
                result = sudo("apt-get install build-essential python-dev ")
                result = sudo("apt-get install python-setuptools")
                result = sudo("easy_install pip")
                result = sudo("pip install --upgrade pip virtualenv virtualenvwrapper")
                with cd(base_dir):
                    result = sudo("mkdir logs",user=user_acc)
                    if result.failed:
                        print("Failed to create log directory!!")
                    else:
                        print("Created log directory in %s",env.hosts)
                    cmd = "echo 'if [ -f /usr/local/bin/virtualenvwrapper.sh ]  \nthen\n source /usr/local/bin/virtualenvwrapper.sh     \nfi \n' >> /home/%s/.bash_profile"%(user_acc)
                    result = sudo(cmd)
                    cmd = 'chown %s /home/%s/.bash_profile'%(user_acc,user_acc)
                    result = sudo(cmd)
                    cmd = 'chgrp %s /home/%s/.bash_profile'%(user_acc,user_acc)
                    result = sudo(cmd)
                    with prefix(". /usr/local/bin/virtualenvwrapper.sh "):
                        execute(su, user_pass, user_acc, 'mkvirtualenv %s'%user_acc)  
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print( "Exception (%s:%s): %s" %(fname,exc_tb.tb_lineno,str(e)))
