# HOW TO UPGRADE
fab deployapp:cfg_file=config.json,server="DEVSERVER1"

#PREREQUISITES:
1)System is already configured. 
2)Table appserver_tenant.database_mappings =>properly set up
3)The django-app is a sudoer and you know the sudoer password(dj123 generally)
4)

#CONFIGS:
{
  "DEVSERVER1": {    # WHICH SERVER ARE WE TARGETING
    "python_app": {                  
      "user_acc":"django-app",   # NO NEED TO MODIFY
      "user_pass":"dj123",       #
      "base_dir":"/home/django-app/", # NO NEED TO MODIFY
      "repo_url":"https://github.com/hirepro/PythonApp.git", #
      "APP_CONFIG" : { 
	      "sess_validation_config" : {       
		      "validate_session" : true,
		      "config_dict"      : {}
	      },
	      "SERVICE_API_ADDR" : "10.0.3.6",   # UPDATE WHICH .NET SERVER?
	      "MY_ADDR" : "10.0.3.99",           # UPDATE WHICH IP ON WHICH PYTHON IS GOING TO RUN
	      "MY_PORT" : 443,                   # UPDATE WHICH PORT?
	      "DEBUG_MODE" : true,               # DEBUG ENABLED?
              "REDIS_CONFIG" : {
                  "SERVER" : "127.0.0.1",        # 
                  "DB_IDX" : 0,                  # REDIS DB INDEX.
                  "PORT"   : 6379,               
                  "TIMEOUT": 10,                 # CONNECTION SOCKET TIMEOUT
                  "TOKEN_PREFIX" : "",           # 
                  "TOKEN_SUFFIX" : "",    
                  "VALUE_FORMAT" : "JSON"        #
              },
      },
      "DATABASES": {
        "default":    {
          "ENGINE": "django.db.backends.mysql",
          "NAME": "appserver_core",
          "HOST": "localhost",
          "USER": "appserver",                   #UPDATE mysql user with which to connect
          "PASSWORD": "data",                    #UPDATE mysql password
          "PORT": "3306"
        },
        "proctoring_default" : {
                "ENGINE": "django.db.backends.mysql",
                "NAME": "hpro_django",
                "USER": "appserver",
                "PASSWORD": "data",
                "HOST": "localhost",
                "PORT": "3306"
        }
      },
      "VIRTUAL_ENV_NAME" : "django-server"      #UPDATE ONLY IF NEEDED....
    }
  }
}
