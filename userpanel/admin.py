from decimal import *
import decimal
from django.utils.html import format_html
from django.urls import path
from django.contrib import admin
from django.http import HttpResponse
from userpanel.models import Earning, Member, Coderequest, Epin, Rewards
from .models import *
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render
import datetime
from django.db.models import Sum
from django.contrib import messages
admin.site.unregister(Group)
admin.site.unregister(User)





def closing_view(request):
    
    if request.method=="POST":
        yes = request.POST.get('yes')
        if yes == 'yes':

            closeDividend()
            closeEarning()
            PayDividend()
            

            # messages.success(request, 'Dividend closing successfully')

        else:
            messages.error(request, 'Error in closing')
            print('Not OK')
    
    return render(request, 'closing.html')

def closeDividend():
    members = Member.objects.filter(topup__gte=0).all()
    dividend = 0
    for m in members:
        if m.staking == 24:
            dividend = 3
        if m.staking == 36:
                dividend = 4
        if m.staking == 48:
                dividend = 5
        if m.staking == 60:
                dividend = 6
        
        monthylydividend = m.topup * dividend / 100
        perdaydividend = monthylydividend / 30
        if perdaydividend > 0:
                
            days = datetime.date.today() - m.topupdate
            totaldividend =  days.days * perdaydividend

            if totaldividend > 0.0:
                
                total = Dividend.objects.filter(userid = m.userid).aggregate(Sum('amount'))
                totalgot = total["amount__sum"]
                totalgot1 = 0 if totalgot is None else totalgot
                print(totaldividend, totalgot1)
                final = float(totaldividend) - float(totalgot1)
                
                if float(final) > 0.0:
                    print(m.userid, float(final))
                    datadi = Dividend(userid = m.userid, amount=final, status= 'Pending')
                    datadi.save()

                    return True
                    
    return True                # print(m.userid, totaldividend, totalgot1, final)



def closeEarning():
    members = Member.objects.all()
    for m in members:
         total = Earning.objects.filter(userid = m.userid, status='Pending').aggregate(Sum('amount'))
         totalearn = total["amount__sum"]
         totalpending = 0 if totalearn is None else totalearn
         finalbalance = 0
         if totalpending > 0:
             
             try:
                  walletbalance = Wallet.objects.filter(userid=m.userid).values_list("balance", flat=True)
                  for bal in walletbalance:
                      finalbalance = float(totalpending) + float(bal)
             except: Wallet.DoesNotExist
             pass

             try:
                Wallet.objects.filter(userid = m.userid).update(balance = finalbalance)
                Earning.objects.filter(userid = m.userid).update(status = 'Paid')
                print(m.userid, totalpending, finalbalance)
                return True

             except:
                 pass


def PayDividend():
    members = Member.objects.all()
    for m in members:
         total = Dividend.objects.filter(userid = m.userid, status='Pending').aggregate(Sum('amount'))
         totalearn = total["amount__sum"]
         totalpending = 0 if totalearn is None else totalearn
         finalbalance = 0
         if totalpending > 0:
             
             try:
                  walletbalance = Wallet.objects.filter(userid=m.userid).values_list("balance", flat=True)
                  for bal in walletbalance:
                      finalbalance = float(totalpending) + float(bal)
             except: Wallet.DoesNotExist
             pass

             try:
                Wallet.objects.filter(userid = m.userid).update(balance = finalbalance)
                Dividend.objects.filter(userid = m.userid).update(status = 'Paid')
                print(m.userid, totalpending, finalbalance)
                return True

             except:
                 pass

class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'userid', 'sponsor', 'Directs', 'dividend', 'Dividend_paid', 'status', 'Earning','Wallet_balance',)
    exclude = ('Action',)
    list_per_page = 100
    search_fields = ('userid',)

    def Earning(self, obj):
        total = Earning.objects.filter(userid = obj.userid).aggregate(Sum('amount'))
        return total["amount__sum"]

    def Dividend_paid(self, obj):
        total = Dividend.objects.filter(userid = obj.userid).aggregate(Sum('amount'))
        return total["amount__sum"]

    def Directs(self, obj):
        return Member.objects.filter(sponsor = obj.userid).count()
    
    def Wallet_balance(self, obj):
        wallet = Wallet.objects.filter(userid = obj.userid).get()
        return wallet.balance

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    # def has_change_permission(self, request, obj=None):
    #     return False


class EpinAdmin(admin.ModelAdmin):
    list_display = ('epin', 'amount','issue_to', 'generate_time', 'used_by', 'used_time', 'status')
    exclude = ('epin','Action','generated_by', 'used_by', 'used_time', 'status')
    list_per_page = 100
    search_fields = ('epin',)
    readonly_fields = ('epin',)
    
    



class RequestcodeAdmin(admin.ModelAdmin):
    list_display = ('userid', 'hash','amount', 'date')
    exclude = ('Action',)
    list_per_page = 50
    search_fields = ('userid',)
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    



class EarningAdmin(admin.ModelAdmin):
    list_display = ('userid', 'amount','type', 'levels', 'ref_id', 'date', 'status')
    list_per_page = 100
    search_fields = ('userid',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    # def has_change_permission(self, request, obj=None):
    #     return False


class MprofileAdmin(admin.ModelAdmin):
    list_display = ('userid','id_proof_tag','add_proof_tag','photo_tag',)
    list_per_page = 100
    search_fields = ('photo',)

class WalletAdmin(admin.ModelAdmin):
    list_display = ('userid','balance',)
    list_per_page = 10
    search_fields = ('userid',)

class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('userid','amount', 'status', 'paid_date', 'trans_detail')
    list_per_page = 10
    search_fields = ('userid',)
    list_filter = ('status',)

class KycAdmin(admin.ModelAdmin):
    list_display = ('userid','id_proof', 'address_proof', 'photo',)
    list_per_page = 100
    search_fields = ('userid',)

class DividendAdmin(admin.ModelAdmin):
    list_display = ('userid','amount','date','status',)
    list_per_page = 100
    exclude = ('Action',)
    search_fields = ('userid',)

    def has_delete_permission(self, request, obj=None):
       return True

    # def has_add_permission(self, request):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False
    
    # def has_change_permission(self, request, obj=None):
    #     return False





class ClosingModel(models.Model):

	class Meta:
		verbose_name_plural = 'Closing'
		app_label = 'userpanel'




class DummyModelAdmin(admin.ModelAdmin):
    model = ClosingModel

    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name)
        return [
            path('settings/', closing_view, name=view_name),
        ]
# Register your models here.

admin.site.disable_action('delete_selected')
admin.site.register(Member, MemberAdmin)
admin.site.register(Coderequest, RequestcodeAdmin)
admin.site.register(Epin, EpinAdmin)
admin.site.register(Rewards)
# admin.site.register(Kyc, KycAdmin)
admin.site.register(Member_profile, MprofileAdmin)
admin.site.register(Earning, EarningAdmin)
admin.site.register(Wallet, WalletAdmin)
# admin.site.register(Dividend, DividendAdmin)
admin.site.register(Widhdraw_requests, WithdrawAdmin)






admin.site.register(ClosingModel, DummyModelAdmin)