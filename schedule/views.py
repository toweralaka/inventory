from django.conf import settings
from django.contrib import messages # add context to HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, reverse
from django.utils import timezone
from django.views.generic.edit import UpdateView

import os

from .models import (MerchantSupply, MerchantReturn, StockReceipt, StockReturned, 
    ItemIssued, ItemRetrieved, DepartmentalProductReceipt, DepartmentalProductSupply)
from .forms import (MerchantSupplyForm, MerchantReturnForm, StockReceiptForm, 
    StockReturnedForm, ItemIssuedForm, ItemRetrievedForm, DepartmentalProductReceiptForm, 
    DepartmentalProductSupplyForm)

# Create your views here.
@login_required
def view_supply(request, pk):
    item = get_object_or_404(MerchantSupply, pk=pk)
    return render(request, 'inventory/item-view.html')

#merchant's interaction with store
@login_required
def merchant_supply_view(request):
    if request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = MerchantSupply.objects.filter(
            merchant=request.user.merchant, confirm_entry=True)
        pending_list = MerchantSupply.objects.filter(
            merchant=request.user.merchant, confirm_entry=False)
        context = {
            'object_list': supplies,
            'pending_list': pending_list,
        }
        return render(request, 'inventory/merchant_supply.html', context)

@login_required
def merchant_confirm_supply(request, pk):
    if request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = MerchantSupply.objects.filter(
            merchant=request.user.merchant, confirm_entry=True)
        supply = get_object_or_404(MerchantSupply, pk=pk)
        if supply.merchant == request.user.merchant:
            form = MerchantSupplyForm(
                request.POST or None, request.FILES or None, instance=supply)
            if request.method == 'POST':
                # form = MerchantSupplyForm(request.POST)
                if form.is_valid():
                    form.save()
                    display_message = "Supply Confirmed!"
                    messages.add_message(request, messages.INFO, display_message)
                    # return HttpResponseRedirect(reverse('assignment:assignment', args=(assignment.id,)))
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list': supplies,
                        'form': form,
                    }
                    return render(request, 'inventory/merchant_confirm_supply.html', context)
            context = {
                'object_list': supplies,
                'form': form,
            }
            return render(request, 'inventory/merchant_confirm_supply.html', context)
        else:
            return HttpResponseRedirect('/')

@login_required
def merchant_return_view(request):
    if request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = MerchantReturn.objects.filter(
            supply__merchant=request.user.merchant, confirm_entry=True)
        pending_list = MerchantReturn.objects.filter(confirm_entry=False)
        context = {
            'object_list': returns,
            'pending_list': pending_list,
        }
        return render(request, 'inventory/merchant_return.html', context)

@login_required
def merchant_confirm_return(request, pk):
    if request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = MerchantReturn.objects.filter(
            supply__merchant=request.user.merchant, confirm_entry=True)
        d_return = get_object_or_404(MerchantReturn, pk=pk)
        if d_return.supply.merchant == request.user.merchant:
            form = MerchantReturnForm(
                request.POST or None, request.FILES or None, instance=d_return)
            if request.method == 'POST':
                # form = MerchantReturnForm(request.POST)
                if form.is_valid():
                    form.save()
                    display_message = "Returns Confirmed!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list': returns,
                        'form': form,
                    }
                    return render(request, 'inventory/merchant_confirm_return.html', context)
            context = {
                'object_list': returns,
                'form': form,
            }
            return render(request, 'inventory/merchant_confirm_return.html', context)
        else:
            return HttpResponseRedirect('/')


#store's interaction with merchant
@login_required
def stock_receipts(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = StockReceipt.objects.all()
        form = StockReceiptForm()
        if request.method == 'POST':
            form = StockReceiptForm(request.POST)
            if form.is_valid():
                new_supply = form.save(commit=False)
                new_supply.officer = request.user.officer
                new_supply.balance = form.cleaned_data['quantity']
                new_supply.save()
                display_message = "Supply Successfully Recorded!"
                messages.add_message(request, messages.INFO, display_message)
                            # return HttpResponseRedirect(reverse('assignment:assignment', args=(assignment.id,)))
                return HttpResponseRedirect('/')
            else:
                context = {
                    'object_list': supplies,
                    'form': form,
                }
                return render(request, 'inventory/stock_receipt.html', context)
        context = {
            'object_list': supplies,
            'form': form,
        }
        return render(request, 'inventory/stock_receipt.html', context)
    

@login_required
def update_stock_receipt(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = StockReceipt.objects.filter(confirm_entry=True)
        receipt = get_object_or_404(StockReceipt, pk=pk)
        if receipt.officer == request.user.officer:
            form = StockReceiptForm(request.POST or None, request.FILES or None, instance=receipt)
            if request.method == 'POST':
                # form = StockReceiptForm(request.POST)
                if form.is_valid():
                    new_supply = form.save(commit=False)
                    new_supply.balance = form.cleaned_data['quantity']
                    new_supply.save()
                    display_message = "Supply Updated!"
                    # receipt.update_merchant()
                    messages.add_message(request, messages.INFO, display_message)
                                # return HttpResponseRedirect(reverse('assignment:assignment', args=(assignment.id,)))
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list': supplies,
                        'form': form,
                    }
                    return render(request, 'inventory/stock_update.html', context)
            context = {
                'object_list': supplies,
                'form': form,
            }
            return render(request, 'inventory/stock_update.html', context)
        else:
            n1 = "\n"
            display_message = (f"{receipt.officer.name} made the entry "
                                f"originally, not you! {n1}Please contact CONTROL.")
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')

@login_required
def stock_return(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = StockReturned.objects.all()
        form = StockReturnedForm()
        if request.method == 'POST':
            form = StockReturnedForm(request.POST)
            if form.is_valid():
                new_supply = form.save(commit=False)
                new_supply.officer = request.user.officer
                # new_supply.balance = form.cleaned_data['quantity']
                new_supply.save()
                display_message = "Returns Successfully Recorded!"
                messages.add_message(request, messages.INFO, display_message)
                            # return HttpResponseRedirect(reverse('assignment:assignment', args=(assignment.id,)))
                return HttpResponseRedirect('/')
            else:
                context = {
                    'object_list': supplies,
                    'form': form,
                }
                return render(request, 'inventory/stock_return.html', context)
        context = {
            'object_list': supplies,
            'form': form,
        }
        return render(request, 'inventory/stock_return.html', context)

@login_required
def update_stock_return(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = StockReturned.objects.filter(confirm_entry=True)
        receipt = get_object_or_404(StockReturned, pk=pk)
        if receipt.officer == request.user.officer:
            form = StockReturnedForm(
                request.POST or None, request.FILES or None, instance=receipt
                )
            if request.method == 'POST':
                if form.is_valid():
                    form.save()                    
                    # new_supply.balance = form.cleaned_data['quantity']
                    # new_supply.save()
                    display_message = "Returns Updated!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list': returns,
                        'form': form,
                    }
                    return render(
                        request, 'inventory/stock_return_update.html', context)
            context = {
                'object_list': returns,
                'form': form,
            }
            return render(request, 'inventory/stock_return_update.html', context)
        else:
            n1 = "\n"
            display_message = (f"{receipt.officer.name} made the entry "
                            f"originally, not you! {n1}Please contact CONTROL.")
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')

#store's interaction with departments
@login_required
def items_issued(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = ItemIssued.objects.all().order_by('date')
        for i in supplies:
            if i.is_new_issue():
                i.save()
        form = ItemIssuedForm()
        if request.method == 'POST':
            form = ItemIssuedForm(request.POST)
            if form.is_valid():
                new_supply = form.save(commit=False)
                new_supply.officer = request.user.officer
                new_supply.save()
                display_message = "Issue Successfully Recorded!"
                messages.add_message(request, messages.INFO, display_message)
                return HttpResponseRedirect('/')
            else:
                context = {
                    'object_list': supplies,
                    'form': form,
                }
                return render(request, 'inventory/items_issued.html', context)
        context = {
            'object_list': supplies,
            'form': form,
        }
        return render(request, 'inventory/items_issued.html', context)

@login_required
def dept_receipt_view(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        receipts = DepartmentalProductReceipt.objects.filter(
            department_officer=request.user.officer,
            confirm_entry= True
            )
        pending_list = DepartmentalProductReceipt.objects.filter(
            department_officer=request.user.officer,
            confirm_entry= False
            )
        context = {
            'object_list': receipts,
            'pending_list': pending_list,
        }
        return render(request, 'inventory/dept_receipts.html', context)

def confirm_dept_receipt(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        receipts = DepartmentalProductReceipt.objects.filter(
            department_officer=request.user.officer
            )
        receipt = get_object_or_404(DepartmentalProductReceipt, pk=pk)
        form = DepartmentalProductReceiptForm(
            request.POST or None, request.FILES or None, instance=receipt
            )
        if request.method == 'POST':
            # form = DepartmentalProductReceiptForm(request.POST)
            if form.is_valid():
                form.save()
                # new_supply = form.save(commit=False)
                # new_supply.officer = request.user.officer
                # # new_supply.balance = form.cleaned_data['quantity']
                # new_supply.save()
                display_message = "Receipt Successfully Confirmed!"
                messages.add_message(request, messages.INFO, display_message)
                return HttpResponseRedirect('/')
            else:
                context = {
                    'object_list': receipts,
                    'form': form,
                }
                return render(request, 'inventory/dept_confirm_receipts.html', context)
        context = {
            'object_list': receipts,
            'form': form,
        }
        return render(request, 'inventory/dept_confirm_receipts.html', context)


@login_required
def items_received(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = ItemRetrieved.objects.filter(officer=request.user.officer)
        form = ItemRetrievedForm()
        if request.method == 'POST':
            form = ItemRetrievedForm(request.POST)
            if form.is_valid():
                new_supply = form.save(commit=False)
                new_supply.officer = request.user.officer
                new_supply.save()
                display_message = "Returns Successfully Recorded!"
                messages.add_message(request, messages.INFO, display_message)
                return HttpResponseRedirect('/')
            else:
                context = {
                    'object_list': returns,
                    'form': form,
                }
                return render(request, 'inventory/items_receipt.html', context)
        context = {
            'object_list': returns,
            'form': form,
        }
        return render(request, 'inventory/items_receipt.html', context)

#departments' interaction with store
@login_required
def dept_return_view(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = DepartmentalProductSupply.objects.filter(
            confirm_entry=True, department_officer=request.user.officer)
        pending_list = DepartmentalProductSupply.objects.filter(
            confirm_entry=False, department_officer=request.user.officer)
        context = {
            'object_list': returns,
            'pending_list': pending_list,
        }
        return render(request, 'inventory/dept_return.html', context)


def dept_confirm_return(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = DepartmentalProductSupply.objects.filter(
            confirm_entry=True, department_officer=request.user.officer)
        d_return = get_object_or_404(DepartmentalProductSupply, pk=pk)
        form = DepartmentalProductSupplyForm()
        if request.method == 'POST':
            form = DepartmentalProductSupplyForm(request.POST)
            if form.is_valid():
                display_message = "Return Successfully Recorded!"
                messages.add_message(request, messages.INFO, display_message)
                return HttpResponseRedirect('/')
            else:
                context = {
                    'object_list':returns,
                    'form': form,
                }
                return render(request, 'inventory/dept_confirm_returns.html', context)
        context = {
            'object_list':returns,
            'form': form,
        }
        return render(request, 'inventory/dept_confirm_returns.html', context)



