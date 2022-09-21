
from decimal import Decimal
from multiprocessing import context
from pprint import pprint
import random
import bcrypt

from unicodedata import decimal, name
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
from userpanel.models import Dividend, Member, Coderequest, Earning, Epin, Kyc, Member_profile, Wallet, Widhdraw_requests
from django.contrib.auth.hashers import make_password, check_password
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
# Create your views here.




def indexpage(request):
    return render(request,'index.html')


@login_required(login_url='/loginUser')
def dashboard(request):
    data = Member.objects.filter(userid=request.user.username)
    data1 = Member.objects.get(userid=request.user.username)
    total = Earning.objects.filter(userid = request.user.username).aggregate(Sum('amount'))
    print(data)
    if(total is not None):
        totearn = total["amount__sum"]
    else:
        totearn = 0.0
    if data1.topupdate is not None:
        d0 = data1.topupdate
        d1 = datetime.datetime.now().date()
        delta = d1 - d0
        
        dividend = data1.topup * data1.dividend / 100
        perday = dividend / 7
        roi = round(delta.days * perday, 2)
    else:
        roi=0.00
    #totaldividend = dividend(request.user.username)
    # print(totaldividend)
    referrals = Member.objects.filter(sponsor = request.user.username).count()
    photo = Kyc.objects.filter(userid=request.user.username)
    earningdata = Earning.objects.filter(userid=request.user.username)
    context = {'username': request.user, 'userdata': data, 'earningdata':earningdata, 'photo': photo, 'earning':totearn, 'referrals':referrals, 'roi':roi}    
    return render(request,'dashboard.html', context)



def dividend(userid):
 
    try:
        data = Member.objects.get(userid=userid)
        if data.topupdate is not None:
            if data.staking == 24:
                dividend = 3
            if data.staking == 36:
                dividend = 4
            if data.staking == 48:
                dividend = 5
            if data.staking == 60:
                dividend = 6
            monthylydividend = float(data.topup) * dividend / 100
            perdaydividend = monthylydividend / 30    
            days = datetime.date.today() - data.topupdate

            return days.days * perdaydividend
        else:
            return True

    except Member.DoesNotExist:
        return 0


@login_required(login_url='/loginUser')
def request_code(request):
    if request.method=="POST":
        userid = request.user.username
        hash_type = request.POST.get('type')
        hash = request.POST.get('hash')
        amount = request.POST.get('amount')
        date = datetime.datetime.now()
        status = 'Pending'
        try:
            data = Coderequest(userid = userid, hash_type=hash_type, hash= hash, amount = amount, date=date, status=status)
            save = data.save()
            messages.success(request, 'Request Submitted Successfully')
        except:
            messages.error(request, 'Request Not Submitted. Please try again')

        # print(save)
        # if data:
        #     messages.success(request, 'Request Submitted Successfully')
        # else:
        #     messages.error(request, 'Request Not Submitted. Please try again')
        context = {'username': request.user}
        return render(request, 'request_code.html', context)    

    else:
        context = {'username': request.user}
        return render(request, 'request_code.html', context)
    

@login_required(login_url='/loginUser')
def unused_codes(request):
    data = Epin.objects.filter(issue_to=request.user.username)
    context = {'username': request.user}
    return render(request, 'unused_codes.html', {'username': context, 'data': data})


@login_required(login_url='/loginUser')
def kyc(request):
    if request.method=="POST":
        id_proof = request.FILES['id_proof']
        address_proof = request.FILES['add_proof']
        photo = request.FILES['photo']        
        kyc = Kyc(userid= request.user.username, id_proof=id_proof, address_proof=address_proof, photo=photo)
        kyc.save()
        context = {'username': request.user}
        print(id_proof)
        data = Kyc.objects.filter(userid=request.user.username)
        return render(request, 'kyc/kyc.html', {'username': context, 'data':data})           

    else:
        data = Kyc.objects.filter(userid=request.user.username)
        context = {'username': request.user}
        return render(request, 'kyc/kyc.html', {'username': context, 'data':data})



@login_required(login_url='/loginUser')
def Profile(request):
    #return render(request, 'profile/profile.html')
    if request.method=="POST":
        address = request.POST['address']
        wallet_address = request.POST['wallet_address']
        password = request.POST['oldpass']
        tax_no = request.POST['tax_no']

        profile_update = Member_profile.objects.filter(userid = request.user.username).update(
            address=address,
            taxnumber = tax_no,
            walletaddress = wallet_address,
        )
        print(profile_update)
       
        
        data = Member_profile.objects.filter(userid=request.user.username)
        context = {'username': request.user}
        return render(request, 'profile/profile.html', {'username': context, 'data':data})           

    else:
        
        data = Member_profile.objects.filter(userid=request.user.username)
        print(data)
        context = {'username': request.user}
        return render(request, 'profile/profile.html', {'username': context, 'data':data})
    
    
    




def used_codes(request):
    return render(request, 'used_codes.html')

def obtain_earnings(request):
    data = Earning.objects.filter(userid=request.user.username)
    return render(request, 'earnings/obtain_earning.html', {'data': data})

def evacuate(request):
    data = Earning.objects.filter(userid=request.user.username)
    wallet = Wallet.objects.filter(userid=request.user.username)
    
    if request.method=="POST":        
        amount = request.POST['amount']
        if float(amount) < 10:
            messages.error(request, 'Invalid detail or some error. Please try again')
            return render(request, 'wallet/evacuate.html',{'username':data, 'wallet':wallet})
        else:
            for balance in wallet:
                if float(balance.balance) > float(amount):
                    restbalance = float(balance.balance) - float(amount)
                    Wallet.objects.filter(userid = request.user.username).update(balance= restbalance)
                    withdraw_enter = Widhdraw_requests(userid = request.user.username, amount = amount, date= datetime.date.today(), status='Pending')
                    withdraw_enter.save()
                    print(restbalance)
                    wallet = Wallet.objects.filter(userid=request.user.username)
                    return render(request, 'wallet/evacuate.html',{'username':data, 'wallet':wallet})

    else:        
        return render(request, 'wallet/evacuate.html',{'username':data, 'wallet':wallet})

def loginUser(request):
    
    if request.method=="POST":        
        userid = request.POST['userid']
        password =  request.POST['password']     
        
        user = authenticate(request, username=userid, password=password)
        
        # return HttpResponse (user)
        if user is not None:
            login(request, user)
            return redirect('/dashboard')
        else:
            return render(request, 'login.html')
    
    else:
        return render(request, 'login.html')



def logoutUser(request):
    logout(request)
    # messages.info(request, "Logged out successfully!")
    return redirect("/loginUser")

def validate_username(request):
    sponsor = request.GET.get('sponsor', None)
    data = {
        'is_taken': Member.objects.filter(userid=sponsor).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'A user with this username already exists.'
    return JsonResponse(data)

def new_referral(request):
    if request.method=="POST":
        name = request.POST.get('name')
        sponsor = request.POST.get('sponsor')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        #staking = request.POST.get('stake')
        # name = request.POST.get('country')
        password = request.POST.get('password')
        userid= random.randint(2345678909800, 9923456789000)
        join_date = datetime.datetime.now()
        status = 'Not Active'

        print(name)

        try:
            user = User(username=userid, email=email, last_login=datetime.datetime.now())
            user.set_password(password)
            user.save()
            
            data = Member(userid = userid,  position=0, join_date= join_date, topup=0, status = status, name=name, email=email, sponsor = sponsor, phone = phone, tokens=0)
            data.save()

            walletEntry = Wallet(userid = userid,  balance = 0)
            walletEntry.save()

            profileEntry = Member_profile(userid = userid)
            profileEntry.save()



            return render(request, 'referrals/success.html', {'name': name, 'userid': userid, 'sponsor':sponsor})
        
        except Exception as e:
            print(e)
            messages.error(request, 'Invalid detail or some error. Please try again')
            return render(request, 'referrals/new_referral.html')

    else:
        return render(request, 'referrals/new_referral.html')

def my_referrals(request):
    context = {'username': request.user}
    data = Member.objects.filter(sponsor=request.user.username)
    return render(request, 'referrals/my_referrals.html', {'username': context,'data':data})


def check_business(userid, i=0):
    data = Member.objects.filter(sponsor=userid)
    countdata = Member.objects.filter(sponsor = userid).aggregate(Sum('topup'))
    if countdata["topup__sum"] is not None:
        i += countdata["topup__sum"]
   
    for d in data:
        if d.userid is not None:

            i = check_business(d.userid, i)

    return i



def new_ticket(request):
    return render(request, 'support/new_ticket.html')

def all_tickets(request):
    return render(request,'support/all_tickets.html')

def topup_account(request):
    if request.method=="POST":
        # level = (20,15,10,10,5,5,5,5,5,5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,)
        level = (5,3,2,1,1)
        
        pin = request.POST.get('topup')
        try:
            pindetail = Epin.objects.get(epin=pin)
            Epin.objects.filter(epin = pin).update(status = 'used', used_by=request.user.username, used_time=datetime.datetime.now())
            
            if pindetail.amount >= 50 and pindetail.amount < 500:
                dividendamount = 3
            if pindetail.amount >= 500 and pindetail.amount < 1000:
                dividendamount = 4
            if pindetail.amount >= 1000 and pindetail.amount < 5000:
                dividendamount = 5
            if pindetail.amount >= 50000:
                dividendamount = 6
            
            Member.objects.filter(userid = request.user.username).update(dividend=dividendamount, topup = float(pindetail.amount), status="Active", topupdate = datetime.datetime.now())
            #print(pindetail.amount)
            sponsor = Member.objects.filter(userid=request.user.username).values_list('sponsor', flat=True)
            fspon = ""
            i = 0
            for spn in sponsor:
                fspon = spn           
                
                for sp in level:
                    
                    if(i == 0):                
                        main_sponsor = fspon                
                    else:
                        main_sponsor = find_level_sponsor(main_sponsor, i)

                        # print(main_sponsor, sp)
                    if main_sponsor is not None:
                        if(sp > 0 ) and (main_sponsor > 0):
                            # print(main_sponsor, sp)
                            # print("pay")
                            pay_earning(main_sponsor, pindetail.amount * sp/100, 'Level Income', i , request.user.username, 'Pending', datetime.datetime.now())
                            print(main_sponsor, sp)
                    
                    i += 1
            
        except Epin.DoesNotExist:
            print("Not Found")
        return redirect('/dashboard')

    else:
        return redirect('/dashboard')


def find_level_sponsor(sponsor, i):

    if (i > 0):
        spon = Member.objects.filter(userid=sponsor).values_list("sponsor", flat=True)
        if spon is None:
            return None
        else:
            i =- 1
            for sponmain in spon:
                if sponmain is not None:
                    return find_level_sponsor(sponmain, i)
    else:
        return sponsor



def pay_earning(userid, amount, type, levels, ref_id, status, date):
    data = Earning(userid = userid, amount=amount, type= type, levels=levels, ref_id=ref_id,status = status, date=date)
    data.save()
    return True

def pay_dividend(userid, amount, date, status):
    data = Dividend(userid = userid, amount=amount, date=date, status = status)
    data.save()
    return True


def closing(request):   
    allmembers = Member.objects.all()
    for members in allmembers:
        if members.topup >0:
            if members.dividend is not None:
                d0 = members.topupdate
                d1 = datetime.datetime.now().date()
                delta = d1 - d0
                
                dividend = members.topup * members.dividend / 100
                perday = dividend / 7
                roi = round(delta.days * perday, 2)
                print(roi)
                
                if roi > 0.00:
                    totdividend = Dividend.objects.filter(userid = members.userid).aggregate(Sum('amount'))
                   
                    if totdividend["amount__sum"] is None:
                        totdivi = round(0,2)
                    else:
                        totdivi = round(totdividend["amount__sum"],2)
                   
                    if roi > totdivi:
                        mainroi = roi - totdivi
                        print(mainroi)
                        if mainroi > 0.00:
                            pay_dividend(members.userid, mainroi, datetime.datetime.now(), 'Pending')
                            pay_level_roi(members.userid,mainroi)
        
    return HttpResponse ("closing done")
    

def pay_level_roi(userid,roiamount):
    level = (20,15,10,10,5,5,5,5,5,5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5)
    sponsor = Member.objects.filter(userid=userid).values_list('sponsor', flat=True)
    #print(sponsor)
    fspon = ""
    i = 0
    for spn in sponsor:
        fspon = spn           
        
        for sp in level:
            
            if(i == 0):                
                main_sponsor = fspon                
            else:
                main_sponsor = find_level_sponsor(main_sponsor, i)

                # print(main_sponsor, sp)
            if main_sponsor is not None:
                if(sp > 0 ) and (main_sponsor > 0):
                    # print(main_sponsor, sp)
                    # print("pay")
                    pay_earning(main_sponsor, roiamount * sp/100, 'Roi Level Income', i , userid, 'Pending', datetime.datetime.now())
                    print(main_sponsor, roiamount*sp/100)
                
            i += 1
    return True