# Databricks notebook source
application_id = "TBD" #  Application (client) ID for the Azure Active Directory application.
client_secret = "TBD"
directory_id = "TBD" # Directory (tenant) ID for the Azure Active Directory application

configs = {
    "fs.azure.account.auth.type": "OAuth",
    "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
    "fs.azure.account.oauth2.client.id": application_id,
    "fs.azure.account.oauth2.client.secret": client_secret,
    "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/" + directory_id + "/oauth2/token"
}

storage_account_name = "datadot1storage"



# COMMAND ----------

def unmountPoint(container_name):
    mount_point = f"/mnt/{container_name}"
    if any(mount.mountPoint == mount_point for mount in dbutils.fs.mounts()):
        print(f"Unmounting {mount_point}")
        dbutils.fs.unmount(mount_point)


def mountPoint(container_name):
    mount_point = f"/mnt/{container_name}"
    unmountPoint(container_name)
    print(f"Mounting {mount_point}")
    dbutils.fs.mount(
        source = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/",
        mount_point = mount_point,
        extra_configs = configs
    )


# COMMAND ----------



mountPoint("bronze")
mountPoint("silver")
