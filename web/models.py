from django.db import models
from django.contrib.auth.models import User
from .helpers import getExodusAddress

# Create your models here.
class MigrationAddress(models.Model):
	tao_address = models.CharField(max_length=34,blank=False)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)

	def create(self,user):
		self.tao_address = getExodusAddress(user.username)
		self.owner=user
		self.save()

class TaoReceived(models.Model):
	migration_address = models.ForeignKey(MigrationAddress, on_delete=models.CASCADE)
	txid = models.CharField(max_length=100, blank=False)
	tot_amt = models.DecimalField(max_digits=14, decimal_places=8)
	tot_fee = models.DecimalField(max_digits=14, decimal_places=8)
	confirmations = models.IntegerField(default=0)
	comment = models.CharField(max_length = 100)
	blocktime = models.IntegerField(default=0)
	account = models.CharField(max_length=50)
	address = models.CharField(max_length=50)
	category = models.CharField(max_length=50)
	amount = models.DecimalField(max_digits=14, decimal_places=8)
	fee = models.DecimalField(max_digits=14, decimal_places=8)
	last_update = models.DateField(auto_now_add=True)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)

class TaoSent(models.Model):
	tao_rec =  models.ForeignKey(TaoReceived, on_delete=models.CASCADE)
	amt = models.DecimalField(max_digits=14, decimal_places=8)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	tx_id = models.CharField(max_length=255,blank=True)