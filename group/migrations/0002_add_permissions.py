from django.db import migrations

permissions = [
	""
]
def create_permissions(apps, schema_editor): 
	Permission = apps.get_model("group", "Permission")
	
	for permission in permissions:
		Permission.objects.create(action = permission)

		
def remove_permissions(apps, schema_editor): 
	Permission = apps.get_model("group", "Permission")
	
	for permission in permissions:
		Permission.objects.filter(action__in = permission).delete()
		
class Migration(migrations.Migration): 
	dependencies = [
		("group", "0001_initial")
	]
	
	operations = [
		migrations.RunPython(create_permissions, remove_permissions)
	]