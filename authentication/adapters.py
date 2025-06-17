from allauth.account.adapter import DefaultAccountAdapter

class EmailAdapter(DefaultAccountAdapter): 
	def send_mail(self, template_prefix, email, context): 
		if "activate_url" in context: 
			key = context["key"]
			context["activate_url"] = f"{os.getenv('FRONTEND_HOST_NAME')}/signup/verify/?key={key}"
		return super().send_mail(template_prefix, email, context)