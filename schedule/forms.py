from django import forms
from django.utils import timezone
from datetime import date, datetime, timedelta

from .models import (MerchantSupply, MerchantReturn, StockReceipt, 
    StockReturned, ItemIssued, ItemRetrieved, DepartmentalProductReceipt, 
    DepartmentalProductSupply, Product)
from userdata.models import Officer

# class AssignmentSubmissionForm(forms.ModelForm):
#     assignment_answer = forms.CharField(widget=CKEditorUploadingWidget())

#     class Meta:
#         model = AssignmentSubmission
#         fields = ['assignment_answer', 'assignment_file']
    # contact_phone = forms.CharField(
    #     widget=forms.TextInput(attrs={'placeholder':'Contact Person Phone Number'
    # , 'class':'input'}))
    # def clean_phone(self):
    #     # Check that phone number is valid
    #     phone = self.cleaned_data.get("phone")
    #     if phone:
    #         try:
    #             int(phone) + 1
    #         except Exception as e:
    #             raise forms.ValidationError("Invalid Phone Number")
    #     return phone
BRANCHES = (
    ('branch1', 'branch1'),
    ('branch2', 'branch2'),
    ('branch3', 'branch3'),
)

class MerchantSupplyForm(forms.ModelForm):
    confirm_entry = forms.BooleanField(required=True)
    receiving_officer = forms.ModelChoiceField(
        queryset=Officer.objects.all(), disabled=True)
    branch = forms.ChoiceField(choices=BRANCHES,
        disabled=True)
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(), disabled=True)
    
    class Meta:
        model = MerchantSupply
        # fields = ('branch', 'product', 'unit_price', 'quantity', 'amount')
        exclude = ('ref_code', 'date', 'merchant', 'verified')



class MerchantReturnForm(forms.ModelForm):
    returning_officer = forms.ModelChoiceField(
        queryset=Officer.objects.all(), disabled=True)
    supply = forms.ModelChoiceField(
        queryset=MerchantSupply.objects.all(), disabled=True)
    confirm_entry = forms.BooleanField(required=True)
    class Meta:
        model = MerchantReturn
        fields = ('supply', 'quantity', 'returning_officer', 'comment', 'confirm_entry')



class StockReceiptForm(forms.ModelForm):
    confirm_entry = forms.BooleanField(required=True)
    class Meta:
        model = StockReceipt
        # fields = ('branch', 'product', 'unit_price', 'quantity', 'amount')
        exclude = ('ref_code', 'date', 'officer', 'balance', 'verified')

    def clean(self):
        cleaned_data = super(StockReceiptForm, self).clean()
        d_branch = cleaned_data.get("branch")
        product = cleaned_data.get("product")
        if self.instance.pk is None:
            all_d_supplies = StockReceipt.objects.filter(branch=d_branch,
                product=product, 
                verified=False)
            for i in all_d_supplies:
                if (timezone.now().date() == i.date.date()):
                    raise forms.ValidationError(
                "An Entry Has Been Made For The Same Department Issue, "
                "You May Edit It To Add This Entry")


# class StockUpdateForm(forms.ModelForm):
#     confirm_entry = forms.BooleanField(required=True)
#     class Meta:
#         model = StockReceipt
#         # fields = ('branch', 'product', 'unit_price', 'quantity', 'amount')
#         exclude = ('ref_code', 'date', 'officer', 'balance', 'verified')
        
#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user')
#         super(StockUpdateForm, self).__init__(*args, **kwargs)
#         self.fields['supply'].queryset = MerchantSupply.objects.filter(
#             merchant=user, verified=True)


class StockReturnedForm(forms.ModelForm):
    confirm_entry = forms.BooleanField(required=True)
    comment = forms.CharField(widget=forms.Textarea(), required=True)
    class Meta:
        model = StockReturned
        exclude = ('ref_code', 'date', 'officer', 'verified')

    def __init__(self, *args, **kwargs):
        super(StockReturnedForm, self).__init__(*args, **kwargs)
        self.fields['stock_receipt'].queryset = StockReceipt.objects.filter(
            verified=True)

    #check that returns do not exceed initial supply
    def clean(self):
        cleaned_data = super(StockReturnedForm, self).clean()
        quantity = cleaned_data.get("quantity")
        d_branch = cleaned_data.get("branch")
        d_supply = cleaned_data.get("stock_receipt")
        # d_supply = StockReceipt.objects.get(pk=int(supply))
        # if quantity > d_supply.balance:
        #     raise forms.ValidationError("You cannot return more than the balance")
        if quantity > d_supply.quantity:
            raise forms.ValidationError(
                "You cannot return more than what was received")
        if self.instance.pk is None:
            all_d_supplies = StockReturned.objects.filter(
                stock_receipt=d_supply, verified=False)
            for i in all_d_supplies:
                if (timezone.now().date() == i.date.date()) and (i.branch == d_branch):
                    raise forms.ValidationError(
                "An Entry Has Been Made For The Same Supply, "
                "You May Edit It To Add This Entry")




class ItemIssuedForm(forms.ModelForm):
    confirm_entry = forms.BooleanField(required=True)
    class Meta:
        model = ItemIssued
        exclude = ('ref_code', 'date', 'officer', 'verified')

    def clean(self):
        cleaned_data = super(ItemIssuedForm, self).clean()
        d_branch = cleaned_data.get("branch")
        product = cleaned_data.get("product")
        if self.instance.pk is None:
            all_d_supplies = ItemIssued.objects.filter(branch=d_branch,
                product=product, 
                verified=False)
            for i in all_d_supplies:
                if (timezone.now().date() == i.date.date()):
                    raise forms.ValidationError(
                "An Entry Has Been Made For The Same Issue To The Department, "
                "You May Edit It To Add This Entry")


class DepartmentalProductReceiptForm(forms.ModelForm):
    officer = forms.ModelChoiceField(
        queryset=Officer.objects.all(), disabled=True)
    branch = forms.ChoiceField(choices=BRANCHES,
        disabled=True)
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(), disabled=True)

    confirm_entry = forms.BooleanField(required=True)
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            "placeholder": "Reason for receiving the item(s)"
            }), 
        required=True
        )
    class Meta:
        model = DepartmentalProductReceipt
        exclude = ('ref_code', 'date', 'department_officer', 'verified')


class ItemRetrievedForm(forms.ModelForm):
    confirm_entry = forms.BooleanField(required=True)
    class Meta:
        model = ItemRetrieved
        exclude = ('ref_code', 'date', 'officer', 'verified')


class DepartmentalProductSupplyForm(forms.ModelForm):
    confirm_entry = forms.BooleanField(required=True)
    class Meta:
        model = DepartmentalProductSupply
        exclude = ('ref_code', 'date', 'officer', 'verified')



