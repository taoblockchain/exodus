import random
import string
import json

from django.shortcuts import render, redirect, reverse
from django.urls.exceptions import NoReverseMatch
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from .forms import LoginForm, SignupForm
from .utils import recover_to_addr
from django.utils.translation import ugettext_lazy as _
from .helpers import makeBurnAddress, getExodusAddress, verifyTransaction, sendTransaction, getMoneySupply, getLastBlock
from .forms import SignupForm
from .models import *
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from decimal import *
from web3 import Web3, HTTPProvider
from eth_utils import to_normalized_address,to_checksum_address,to_hex

w3 = Web3(Web3.HTTPProvider(settings.TAO_RPC))

STARTING_SWAP = 16837242.5631325745

def logout_view(request):
	logout(request)
	return redirect('/signup')

def web_login(request):
	if not request.user.is_authenticated:
		return render(request, 'web3auth/login.html')
	else:
		return redirect('/accounts/profile')

def auto_login(request):
	if not request.user.is_authenticated:
		return render(request, 'web3auth/autologin.html')
	else:
		return redirect('/accounts/profile')

def account_profile(request):
	if not request.user.is_authenticated:
		return render(request, 'web3auth/autologin.html')
	addr, created = MigrationAddress.objects.get_or_create(owner=request.user)
	if created:
		addr.create(request.user)
	return render(request, 'accounts/profile.html')

@require_http_methods(["GET"])
def pageDataApi(request):
	if not request.user.is_authenticated:
		return JsonResponse({'success':False})
	addr, created = MigrationAddress.objects.get_or_create(owner=request.user)
	if created:
		addr.create(request.user)
	r = TaoReceived.objects.filter(address=addr.tao_address).aggregate(Sum('amount'))
	s = TaoSent.objects.filter(owner=request.user).aggregate(Sum('amt'))
	ids=[]
	sent_data = []
	tx_=TaoSent.objects.filter(owner=request.user).all()
	for tx in tx_:
		ids.append(tx.tao_rec.id)
		q = [tx.amt,tx.tx_id,tx.tao_rec.amount,tx.tao_rec.txid]
		sent_data.append(q)
	z = TaoReceived.objects.filter(owner=request.user).exclude(id__in=ids).values('amount','txid')
	us_data = []
	for tx in z:
		q = [tx.amount,tx.txid]
		us_data.append(q)
	hot_balance = w3.fromWei(w3.eth.getBalance(settings.SWAP_ADDR),'ether')
	cold_balance = w3.fromWei(w3.eth.getBalance('0x92ef21492f31eeE0BC2C9573C3c4DCF0B3C1C312'),'ether')
	swap_balance = float(hot_balance) + float(cold_balance)
	money_supply = float(getMoneySupply())
	exodus_swap = float(STARTING_SWAP) - swap_balance
	pre_exodus_swap = money_supply - STARTING_SWAP
	total_swapped = pre_exodus_swap + exodus_swap
	percent_swapped = float((total_swapped / money_supply) * 100)
	last_block, last_block_time = getLastBlock()
	data = {
		'copyTarget':addr.tao_address,
		'total_received':r['amount__sum'] if r['amount__sum'] is not None else 0.0,
		'total_sent':s['amt__sum'] if s['amt__sum'] is not None else 0.0,
		'transactions': { 
							'data':sent_data,
						},
		'unsent_transactions':{
								'data':us_data,
							},
		'hot_balance':hot_balance,
		'cold_balance':cold_balance,
		'money_supply':money_supply,
		'swap_balance':swap_balance,
		'exodus_swap':exodus_swap,
		'pre_exodus_swap':pre_exodus_swap,
		'total_swapped':total_swapped,
		'percent_swapped':percent_swapped,
		'last_block':last_block,
		'last_block_time':last_block_time,
	}
	return JsonResponse(data)
	
@require_http_methods(["GET", "POST"])
@csrf_exempt
def wallet_notify(request):
	tx_info = request.POST
	# verify transactions
	for tx in tx_info:
		t = verifyTransaction(tx)
		if t is not None:
			# Make sure it's not a mempool notification
			if 'blocktime' in t:
				for detail in t['details']:
					if (detail['category'] == 'send') or (detail['category'] == 'receive'):
						try:
							found = MigrationAddress.objects.get(tao_address=detail['address'])
						except:
							found = None
						if found is not None:
							# It's in a block and not from the mempool
							#if 'fee' in detail:
							rec, created = TaoReceived.objects.get_or_create(txid = t['txid'], defaults={
							'migration_address' : found,
							'txid' : t['txid'],
							'tot_amt' : 0,
							'tot_fee' : 0,
							'confirmations' : 1,
							'comment' : '',
							'blocktime' : t['blocktime'],
							'account' : detail['account'],
							'address' : detail['address'],
							'category' : detail['category'],
							'amount' : abs(float(detail['amount'])),
							'fee' : 0.0,
							'owner' : found.owner,
							})
							rec.save()
							if created:
								rec.save()
							else:
								# already processed
								return JsonResponse({'success': False })
							# Add 15%
							amount = rec.amount + (rec.amount * .15)
							print('TRANSACTION FOUND IN BLOCK SENDING {0} TAO 2.0'.format(amount))
							sent = sendTransaction(found.owner.username,amount,rec)
							print(sent)
							import time
							time.sleep(7)
							if sent:
								return JsonResponse({'success': True })
							#else:
								# wrong category
							#	return JsonResponse({'success': False })
						else:
							# not found
							return JsonResponse({'success': False })
					else:
						# bad category
						return JsonResponse({'success': False })
			else:
				# mempool, not a block
				return JsonResponse({'success': False })
		else:
			# oooo someone is cheating!
			return JsonResponse({'success': False })

@require_http_methods(["GET", "POST"])
def signup_view(request, template_name='web3auth/signup.html'):
	"""
	1. Creates an instance of a SignupForm.
	2. Checks if the registration is enabled.
	3. If the registration is closed or form has errors, returns form with errors
	4. If the form is valid, saves the user without saving to DB
	5. Sets the user address from the form, saves it to DB
	6. Logins the user using web3auth.backend.Web3Backend
	7. Redirects the user to LOGIN_REDIRECT_URL or 'next' in get or post params
	:param request: Django request
	:param template_name: Template to render
	:return: rendered template with form
	"""
	if request.user.is_authenticated:
		return redirect('/accounts/profile')
	form = SignupForm()
	if not settings.WEB3AUTH_SIGNUP_ENABLED:
		form.add_error(None, _("Sorry, signup's are currently disabled"))
	else:
		if request.method == 'POST':
			form = SignupForm(request.POST)
			if form.is_valid():
				user = form.save(commit=False)
				addr_field = settings.WEB3AUTH_USER_ADDRESS_FIELD
				setattr(user, addr_field, form.cleaned_data[addr_field])
				user.save()
				login(request, user, 'web.backend.Web3Backend')
				return redirect(get_redirect_url(request))
	return render(request,
				  template_name,
				  {'form': form})

def get_redirect_url(request):
	if request.GET.get('next'):
		return request.GET.get('next')
	elif request.POST.get('next'):
		return request.POST.get('next')
	elif settings.LOGIN_REDIRECT_URL:
		try:
			url = reverse(settings.LOGIN_REDIRECT_URL)
		except NoReverseMatch:
			url = settings.LOGIN_REDIRECT_URL
		return url

@require_http_methods(["GET"])
def burn_address_api(request):
	if not request.user:
		return JsonResponse({'success': False, 'error': error})
	template = "A" + request.user.username
	address = getExodusAddress()
	return JsonResponse({'success': True, 'burn_address': str(address)})
	

@require_http_methods(["GET", "POST"])
def login_api(request):
	if request.method == 'GET':
		token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(32))
		request.session['login_token'] = token
		return JsonResponse({'data': token, 'success': True})
	else:
		token = request.session.get('login_token')
		if not token:
			return JsonResponse({'error': _(
				"No login token in session, please request token again by sending GET request to this url"),
				'success': False})
		else:
			form = LoginForm(token, request.POST)
			if form.is_valid():
				signature, address = form.cleaned_data.get("signature"), form.cleaned_data.get("address")
				del request.session['login_token']
				user = authenticate(request, token=token, address=address, signature=signature)
				if user:
					login(request, user, 'web.backend.Web3Backend')

					return JsonResponse({'success': True, 'redirect_url': get_redirect_url(request)})
				else:
					error = _("Can't find a user for the provided signature with address {address}").format(
						address=address)
					return JsonResponse({'success': False, 'error': error})
			else:
				return JsonResponse({'success': False, 'error': json.loads(form.errors.as_json())})


@require_http_methods(["POST"])
def signup_api(request):
	if not settings.WEB3AUTH_SIGNUP_ENABLED:
		return JsonResponse({'success': False, 'error': _("Sorry, signup's are currently disabled")})
	form = SignupForm(request.POST)
	if form.is_valid():
		user = form.save(commit=False)
		addr_field = settings.WEB3AUTH_USER_ADDRESS_FIELD
		setattr(user, addr_field, form.cleaned_data[addr_field])
		user.save()
		login(request, user, 'web.backend.Web3Backend')
		return JsonResponse({'success': True, 'redirect_url': get_redirect_url(request)})
	else:
		return JsonResponse({'success': False, 'error': json.loads(form.errors.as_json())})


