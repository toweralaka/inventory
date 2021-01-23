from django.conf import settings
from django.contrib import messages # add context to HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models, transaction
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, reverse
from django.utils import timezone
from django.views.generic.edit import UpdateView

import csv
import os

from .models import (MerchantSupply, MerchantReturn, StockReceipt, StockReturned, 
    ItemIssued, ItemRetrieved, DepartmentalProductReceipt, DepartmentalProductSupply,
    Merchant, FileBank, Product, ProductStock)
from .forms import (MerchantSupplyForm, MerchantReturnForm, StockReceiptForm, 
    StockReturnedForm, ItemIssuedForm, ItemRetrievedForm, DepartmentalProductReceiptForm, 
    DepartmentalProductSupplyForm, ControlDeleteForm, ItemIssueForm, MerchantForm, 
    StaffForm, ProductImportForm)
from userdata.models import Officer

User = get_user_model()
# Create your views here.

# @login_required
# def view_supply(request, pk):
#     item = get_object_or_404(MerchantSupply, pk=pk)
#     return render(request, 'schedule/item-view.html')

#merchant's interaction with store
@login_required
def merchant_supply_view(request):
    if request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = MerchantSupply.show_objects.filter(
            merchant=request.user.merchant, confirm_entry=True).order_by('-date')
        pending_list = MerchantSupply.show_objects.filter(
            merchant=request.user.merchant, confirm_entry=False).order_by('-date')
        context = {
            'object_list': supplies,
            'pending_list': pending_list,
        }
        return render(request, 'schedule/merchant_supply.html', context)

@login_required
def merchant_confirm_supply(request, pk):
    if request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = MerchantSupply.show_objects.filter(
            merchant=request.user.merchant, confirm_entry=True).order_by('-date')
        supply = get_object_or_404(MerchantSupply, pk=pk)
        if supply.merchant == request.user.merchant:
            form = MerchantSupplyForm(
                request.POST or None, request.FILES or None, instance=supply)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    display_message = "Supply Confirmed!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list': supplies,
                        'form': form,
                    }
                    return render(request, 'schedule/merchant_confirm_supply.html', context)
            context = {
                'object_list': supplies,
                'form': form,
            }
            return render(request, 'schedule/merchant_confirm_supply.html', context)
        else:
            return HttpResponseRedirect('/')

@login_required
def merchant_return_view(request):
    if request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = MerchantReturn.show_objects.filter(
            supply__merchant=request.user.merchant, confirm_entry=True).order_by('-date')
        pending_list = MerchantReturn.show_objects.filter(
            supply__merchant=request.user.merchant,
            confirm_entry=False).order_by('-date')
        context = {
            'object_list': returns,
            'pending_list': pending_list,
        }
        return render(request, 'schedule/merchant_return.html', context)

@login_required
def merchant_confirm_return(request, pk):
    if request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = MerchantReturn.show_objects.filter(
            supply__merchant=request.user.merchant, confirm_entry=True).order_by('-date')
        d_return = get_object_or_404(MerchantReturn, pk=pk)
        if d_return.supply.merchant == request.user.merchant:
            form = MerchantReturnForm(
                request.POST or None, request.FILES or None, instance=d_return)
            if request.method == 'POST':
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
                    return render(
                        request, 'schedule/merchant_confirm_return.html', context)
            context = {
                'object_list': returns,
                'form': form,
            }
            return render(request, 'schedule/merchant_confirm_return.html', context)
        else:
            return HttpResponseRedirect('/')


#store's interaction with merchant
@login_required
def stock_receipts(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = StockReceipt.show_objects.all().order_by('-date')
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
                return render(request, 'schedule/stock_receipt.html', context)
        context = {
            'object_list': supplies,
            'form': form,
        }
        return render(request, 'schedule/stock_receipt.html', context)
    

@login_required
def update_stock_receipt(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        supplies = StockReceipt.show_objects.filter(confirm_entry=True).order_by('-date')
        receipt = get_object_or_404(StockReceipt, pk=pk)
        if receipt.officer == request.user.officer:
            form = StockReceiptForm(
                request.POST or None, request.FILES or None, instance=receipt)
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
                    return render(request, 'schedule/stock_update.html', context)
            context = {
                'object_list': supplies,
                'form': form,
            }
            return render(request, 'schedule/stock_update.html', context)
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
        supplies = StockReturned.show_objects.all().order_by('-date')
        form = StockReturnedForm()
        if request.method == 'POST':
            form = StockReturnedForm(request.POST)
            if form.is_valid():
                new_supply = form.save(commit=False)
                new_supply.officer = request.user.officer
                new_supply.save()
                display_message = "Returns Successfully Recorded!"
                messages.add_message(request, messages.INFO, display_message)
                return HttpResponseRedirect('/')
            else:
                context = {
                    'object_list': supplies,
                    'form': form,
                }
                return render(request, 'schedule/stock_return.html', context)
        context = {
            'object_list': supplies,
            'form': form,
        }
        return render(request, 'schedule/stock_return.html', context)

@login_required
def update_stock_return(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = StockReturned.show_objects.filter(confirm_entry=True).order_by('-date')
        receipt = get_object_or_404(StockReturned, pk=pk)
        if receipt.officer == request.user.officer:
            form = StockReturnedForm(
                request.POST or None, request.FILES or None, instance=receipt
                )
            if request.method == 'POST':
                if form.is_valid():
                    form.save()                    
                    display_message = "Returns Updated!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list': returns,
                        'form': form,
                    }
                    return render(
                        request, 'schedule/stock_return_update.html', context)
            context = {
                'object_list': returns,
                'form': form,
            }
            return render(request, 'schedule/stock_return_update.html', context)
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
        supplies = ItemIssued.show_objects.all().order_by('-date')
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
                return render(request, 'schedule/items_issued.html', context)
        context = {
            'object_list': supplies,
            'form': form,
        }
        return render(request, 'schedule/items_issued.html', context)

@login_required
def dept_receipt_view(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        receipts = DepartmentalProductReceipt.show_objects.filter(
            department_officer=request.user.officer,
            confirm_entry= True
            ).order_by('-date')
        pending_list = DepartmentalProductReceipt.show_objects.filter(
            department_officer=request.user.officer,
            confirm_entry= False
            ).order_by('-date')
        context = {
            'object_list': receipts,
            'pending_list': pending_list,
        }
        return render(request, 'schedule/dept_receipts.html', context)

def confirm_dept_receipt(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        receipts = DepartmentalProductReceipt.show_objects.filter(
            department_officer=request.user.officer
            ).order_by('-date')
        receipt = get_object_or_404(DepartmentalProductReceipt, pk=pk)
        if receipt.department_officer == request.user.officer:
            form = DepartmentalProductReceiptForm(
                request.POST or None, request.FILES or None, instance=receipt
                )
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    display_message = "Receipt Successfully Confirmed!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list': receipts,
                        'form': form,
                    }
                    return render(request, 'schedule/dept_confirm_receipts.html', context)
            context = {
                'object_list': receipts,
                'form': form,
            }
            return render(request, 'schedule/dept_confirm_receipts.html', context)
        else:
            n1 = "\n"
            display_message = (f"{receipt.department_officer.name} made the entry "
                            f"originally, not you! {n1}Please contact CONTROL.")
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')

@login_required
def update_items_issued(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        issues = ItemIssued.show_objects.filter(confirm_entry=True).order_by('-date')
        issue = get_object_or_404(ItemIssued, pk=pk)
        if issue.officer == request.user.officer:
            form = ItemIssuedForm(
                request.POST or None, request.FILES or None, instance=issue
                )
            if request.method == 'POST':
                if form.is_valid():
                    form.save()                    
                    display_message = "Item(s) Issue Updated!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list': issues,
                        'form': form,
                    }
                    return render(
                        request, 'schedule/item_issue_update.html', context)
            context = {
                'object_list': issues,
                'form': form,
            }
            return render(request, 'schedule/item_issue_update.html', context)
        else:
            n1 = "\n"
            display_message = (f"{issue.officer.name} made the entry "
                            f"originally, not you! {n1}Please contact CONTROL.")
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')

@login_required
def items_received(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = ItemRetrieved.show_objects.all().order_by('-date')
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
                return render(request, 'schedule/items_receipt.html', context)
        context = {
            'object_list': returns,
            'form': form,
        }
        return render(request, 'schedule/items_receipt.html', context)

#departments' interaction with store
@login_required
def dept_return_view(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = DepartmentalProductSupply.show_objects.filter(
            confirm_entry=True, 
            department_officer=request.user.officer).order_by('-date')
        pending_list = DepartmentalProductSupply.show_objects.filter(
            confirm_entry=False, 
            department_officer=request.user.officer).order_by('-date')
        context = {
            'object_list': returns,
            'pending_list': pending_list,
        }
        return render(request, 'schedule/dept_returns.html', context)


def confirm_dept_return(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        returns = DepartmentalProductSupply.show_objects.filter(
            confirm_entry=True, 
            department_officer=request.user.officer).order_by('-date')
        d_return = get_object_or_404(DepartmentalProductSupply, pk=pk)
        if d_return.department_officer == request.user.officer:
            form = DepartmentalProductSupplyForm(
                request.POST or None, request.FILES or None, instance=d_return
            )
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    display_message = "Return Successfully Recorded!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list':returns,
                        'form': form,
                    }
                    return render(request, 'schedule/dept_confirm_returns.html', context)
            context = {
                'object_list':returns,
                'form': form,
            }
            return render(request, 'schedule/dept_confirm_returns.html', context)
        else:
            n1 = "\n"
            display_message = (f"{receipt.department_officer.name} made the entry "
                            f"originally, not you! {n1}Please contact CONTROL.")
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')

@login_required
def update_items_received(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        receipts = ItemRetrieved.show_objects.filter(
            confirm_entry=True).order_by('-date')
        receipt = get_object_or_404(ItemRetrieved, pk=pk)
        if receipt.officer == request.user.officer:
            form = ItemRetrievedForm(
                request.POST or None, request.FILES or None, instance=receipt
                )
            if request.method == 'POST':
                if form.is_valid():
                    form.save()                    
                    display_message = "Receipts Updated!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                        'object_list': receipts,
                        'form': form,
                    }
                    return render(
                        request, 'schedule/items_received_update.html', context)
            context = {
                'object_list': receipts,
                'form': form,
            }
            return render(request, 'schedule/items_received_update.html', context)
        else:
            n1 = "\n"
            display_message = (f"{receipt.officer.name} made the entry "
                            f"originally, not you! {n1}Please contact CONTROL.")
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')

@login_required
def control_view_supply(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        object_list = StockReceipt.show_objects.all().order_by('-date')
        context = {
            'object_list': object_list,
        }
        return render(request, 'schedule/ctrl_view_supply.html', context)

@login_required
def control_view_return(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        object_list = StockReturned.show_objects.all().order_by('-date')
        context = {
            'object_list': object_list,
        }
        return render(request, 'schedule/ctrl_view_return.html', context)

@login_required
def control_view_issue(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        object_list = ItemIssued.show_objects.all().order_by('-date')
        context = {
            'object_list': object_list,
        }
        return render(request, 'schedule/ctrl_view_issue.html', context)

@login_required
def control_view_dept_return(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        object_list = ItemRetrieved.show_objects.all().order_by('-date')
        context = {
            'object_list': object_list,
        }
        return render(request, 'schedule/ctrl_view_dept_return.html', context)

@login_required
def control_delete_supply(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        object_list = StockReceipt.show_objects.all().order_by('-date')
        item = get_object_or_404(StockReceipt, pk=pk)
        item_pair = MerchantSupply.show_objects.get(ref_code=item.ref_code)
        form = ControlDeleteForm()
        if request.method == 'POST':
            form = ControlDeleteForm(request.POST)
            if form.is_valid():
                if (item.ref_code).lower() == (form.cleaned_data['ref_code']).lower():
                    item.hidden_by = request.user.officer
                    item.hide = True
                    item.hide_reason = form.cleaned_data['hide_reason']
                    item.save()
                    item_pair.hidden_by = request.user.officer
                    item_pair.hide = True
                    item_pair.hide_reason = form.cleaned_data['hide_reason']
                    item_pair.save()
                    display_message = "'Delete' Successful!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                    'item': item,
                    'object_list': object_list,
                    'form': form,
                    'display_message': "Invalid Ref Code!"
                }
                return render(request, 'schedule/ctrl_del_supply.html', context)
            else:
                context = {
                    'item': item,
                    'object_list': object_list,
                    'form': form,
                }
                return render(request, 'schedule/ctrl_del_supply.html', context)
        context = {
            'item': item,
            'object_list': object_list,
            'form': form,
        }
        return render(request, 'schedule/ctrl_del_supply.html', context)

@login_required
def control_delete_return(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        object_list = StockReturned.show_objects.all().order_by('-date')
        item = get_object_or_404(StockReturned, pk=pk)
        item_pair = MerchantReturn.show_objects.get(ref_code=item.ref_code)
        form = ControlDeleteForm()
        if request.method == 'POST':
            form = ControlDeleteForm(request.POST)
            if form.is_valid():
                if (item.ref_code).lower() == (form.cleaned_data['ref_code']).lower():
                    item.hidden_by = request.user.officer
                    item.hide = True
                    item.hide_reason = form.cleaned_data['hide_reason']
                    item.save()
                    item_pair.hidden_by = request.user.officer
                    item_pair.hide = True
                    item_pair.hide_reason = form.cleaned_data['hide_reason']
                    item_pair.save()
                    display_message = "'Delete' Successful!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                    'item': item,
                    'object_list': object_list,
                    'form': form,
                    'display_message': "Invalid Ref Code!"
                }
                return render(request, 'schedule/ctrl_del_return.html', context)
            else:
                context = {
                    'item': item,
                    'object_list': object_list,
                    'form': form,
                }
                return render(request, 'schedule/ctrl_del_return.html', context)
        context = {
            'item': item,
            'object_list': object_list,
            'form': form,
        }
        return render(request, 'schedule/ctrl_del_return.html', context)

@login_required
def control_delete_issue(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        object_list = ItemIssued.show_objects.all().order_by('-date')
        item = get_object_or_404(ItemIssued, pk=pk)
        item_pair = DepartmentalProductReceipt.show_objects.get(ref_code=item.ref_code)
        form = ControlDeleteForm()
        if request.method == 'POST':
            form = ControlDeleteForm(request.POST)
            if form.is_valid():
                if (item.ref_code).lower() == (form.cleaned_data['ref_code']).lower():
                    item.hidden_by = request.user.officer
                    item.hide = True
                    item.hide_reason = form.cleaned_data['hide_reason']
                    item.save()
                    item_pair.hidden_by = request.user.officer
                    item_pair.hide = True
                    item_pair.hide_reason = form.cleaned_data['hide_reason']
                    item_pair.save()
                    display_message = "'Delete' Successful!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                    'item': item,
                    'object_list': object_list,
                    'form': form,
                    'display_message': "Invalid Ref Code!"
                }
                return render(request, 'schedule/ctrl_del_issue.html', context)
            else:
                context = {
                    'item': item,
                    'object_list': object_list,
                    'form': form,
                }
                return render(request, 'schedule/ctrl_del_issue.html', context)
        context = {
            'item': item,
            'object_list': object_list,
            'form': form,
        }
        return render(request, 'schedule/ctrl_del_issue.html', context)

@login_required
def control_delete_dept_return(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        object_list = ItemRetrieved.show_objects.all().order_by('-date')
        item = get_object_or_404(ItemRetrieved, pk=pk)
        item_pair = DepartmentalProductSupply.show_objects.get(ref_code=item.ref_code)
        form = ControlDeleteForm()
        if request.method == 'POST':
            form = ControlDeleteForm(request.POST)
            if form.is_valid():
                if (item.ref_code).lower() == (form.cleaned_data['ref_code']).lower():
                    item.hidden_by = request.user.officer
                    item.hide = True
                    item.hide_reason = form.cleaned_data['hide_reason']
                    item.save()
                    item_pair.hidden_by = request.user.officer
                    item_pair.hide = True
                    item_pair.hide_reason = form.cleaned_data['hide_reason']
                    item_pair.save()
                    display_message = "'Delete' Successful!"
                    messages.add_message(request, messages.INFO, display_message)
                    return HttpResponseRedirect('/')
                else:
                    context = {
                    'item': item,
                    'object_list': object_list,
                    'form': form,
                    'display_message': "Invalid Ref Code!"
                }
                return render(request, 'schedule/ctrl_del_dept_return.html', context)
            else:
                context = {
                    'item': item,
                    'object_list': object_list,
                    'form': form,
                }
                return render(request, 'schedule/ctrl_del_dept_return.html', context)
        context = {
            'item': item,
            'object_list': object_list,
            'form': form,
        }
        return render(request, 'schedule/ctrl_del_dept_return.html', context)

# @login_required
# def control_view_supply(request, pk):
#     if not request.user.is_staff:
#         return HttpResponseRedirect('/accounts/logout/')
#     else:

@login_required
def view_stock_use(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    else:
        item_list = ItemIssued.show_objects.all().order_by('-date')
        form = ItemIssueForm()
        if request.method == 'POST':
            form = ItemIssueForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                branch = form.cleaned_data['branch']
                period = f"{start_date} To {end_date} In {branch}"
                item_list = ItemIssued.show_objects.filter(branch=branch,
                    date__gte=start_date, date__lte=end_date
                    ).order_by('date')
                print(end_date)
                print(item_list[0].date)
                if 'export' in request.POST:
                    # Create the HttpResponse object with the appropriate CSV header.
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="items issued.csv"'
                    writer = csv.writer(response)
                    writer.writerow(['Date', 'Product', 'Quantity', 'Unit Price', 'Amount'])
                    for i in item_list:
                        writer.writerow([i.date.date(), i.product, i.quantity, i.get_unit_price(), i.get_amount()])
                    return response
                else:
                    context = {
                        'period': period,
                        'object_list': item_list,
                        'form': form,
                    }
                    return render(request, 'schedule/ctrl_view_stock_use.html', context)
            else:
                context = {
                'object_list': item_list,
                'form': form,
            }
            return render(request, 'schedule/ctrl_view_stock_use.html', context)
        context = {
            'object_list': item_list,
            'form': form,
        }
        return render(request, 'schedule/ctrl_view_stock_use.html', context)

def merchant_signup(request):
    form = MerchantForm()
    if request.method == 'POST':
        form = MerchantForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                merchant = Merchant(
                    user = user,
                    name = form.cleaned_data['name'],
                    phone_number = form.cleaned_data['phone_number'],
                    email_address = form.cleaned_data['email_address'],
                    address = form.cleaned_data['address'],
                    liaison_officer = form.cleaned_data['liaison_officer'],
                    liaison_officer_salutation = form.cleaned_data['liaison_officer_salutation'],
                    active = False,
                    )
                merchant.save()
                for prod in form.cleaned_data['products']:
                    merchant.products.add(prod)
                merchant.save()
            return HttpResponseRedirect('/accounts/login/')
        else:
            return render(request, 'schedule/merchant_signup.html', {'form': form,})
    return render(request, 'schedule/merchant_signup.html', {'form': form,})

def staff_signup(request):
    form = StaffForm()
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                officer = Officer(
                    user = user,
                    name = form.cleaned_data['name'],
                    phone_number = form.cleaned_data['phone_number'],
                    email_address = form.cleaned_data['email_address'],
                    employee_code = form.cleaned_data['employee_code'],
                    branch = form.cleaned_data['branch'],
                    department = form.cleaned_data['department'],
                    details = form.cleaned_data['details'],
                    active=False
                    )
                officer.save()
            return HttpResponseRedirect('/accounts/login/')
        else:
            return render(request, 'schedule/staff_signup.html', {'form': form,})
    return render(request, 'schedule/staff_signup.html', {'form': form,})

@login_required
def ctrl_create_staff(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    form = StaffForm()
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                officer = Officer(
                    user = user,
                    name = form.cleaned_data['name'],
                    phone_number = form.cleaned_data['phone_number'],
                    email_address = form.cleaned_data['email_address'],
                    employee_code = form.cleaned_data['employee_code'],
                    branch = form.cleaned_data['branch'],
                    department = form.cleaned_data['department'],
                    details = form.cleaned_data['details'],
                    )
                officer.save()
            display_message = "Staff Creation Successful!"
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'schedule/ctrl_create_staff.html', {'form': form,})
    return render(request, 'schedule/ctrl_create_staff.html', {'form': form,})

@login_required
def ctrl_create_merchant(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    form = MerchantForm()
    if request.method == 'POST':
        form = MerchantForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                merchant = Merchant(
                    user = user,
                    name = form.cleaned_data['name'],
                    phone_number = form.cleaned_data['phone_number'],
                    email_address = form.cleaned_data['email_address'],
                    address = form.cleaned_data['address'],
                    liaison_officer = form.cleaned_data['liaison_officer'],
                    liaison_officer_salutation = form.cleaned_data['liaison_officer_salutation'],
                    active=True
                    )
                merchant.save()
                for prod in form.cleaned_data['products']:
                    merchant.products.add(prod)
                merchant.save()
            display_message = "Merchant Creation Successful!"
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'schedule/ctrl_create_merchant.html', {'form': form,})
    return render(request, 'schedule/ctrl_create_merchant.html', {'form': form,})

@login_required
def pending_users(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    officer_list = Officer.objects.filter(active=False)
    merchant_list = Merchant.objects.filter(active=False)
    context = {
        'officer_list': officer_list,
        'merchant_list': merchant_list,
        }
    return render(request, 'schedule/ctrl_view_users.html', context)

@login_required
def activate_user(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    user = get_object_or_404(User, pk=pk)
    try:
        merchant = Merchant.objects.get(user=user)
        officer = None
        status = 'Merchant'
    except Merchant.DoesNotExist:
        officer = Officer.objects.get(user=user)
        merchant = None
        status = 'Officer'
    except Officer.DoesNotExist:
        return Http404
    if request.method == 'POST':
        if request.POST.get('confirm') == 'on':
            if officer is not None:
                officer.active = True
                officer.save()
            else:
                merchant.active = True
                merchant.save()
            display_message = "Activation Successful!"
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')
    context = {
        'officer': officer,
        'merchant': merchant,
        'status': status,
        }
    return render(request, 'schedule/ctrl_activate_user.html', context)

@login_required
def delete_user(request, pk):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    user = get_object_or_404(User, pk=pk)
    try:
        merchant = Merchant.objects.get(user=user)
        officer = None
        status = 'Merchant'
    except Merchant.DoesNotExist:
        officer = Officer.objects.get(user=user)
        merchant = None
        status = 'Officer'
    except Officer.DoesNotExist:
        return Http404
    if request.method == 'POST':
        if request.POST.get('confirm') == 'on':
            if officer is not None:
                with transaction.atomic():
                    officer.delete()
                    user.delete()
            else:
                merchant.delete()
                user.delete()
            display_message = "Delete Successful!"
            messages.add_message(request, messages.INFO, display_message)
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')
    context = {
        'officer': officer,
        'merchant': merchant,
        'status': status,
        }
    return render(request, 'schedule/ctrl_delete_user.html', context)

@login_required
def import_db(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    form = ProductImportForm()
    object_list = []
    if request.method == 'POST':
        form = ProductImportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            file_name = form.cleaned_data['file_name']
            branch = form.cleaned_data['branch']
            try:
                dfile = FileBank.objects.get(file_name=file_name)
            except Exception:
                display_message = "INVALID FILENAME!"
                context = {
                    'form': form,
                    'display_message': display_message
                    }
                return render(request, 'schedule/ctrl_importdb.html', context)
            else:
                parturl = dfile.the_file
                fileurl = os.path.join(settings.MEDIA_ROOT, str(parturl))
                with open(str(fileurl)) as f:
                    reader = csv.reader(f)
                    for row in reader:
                        try:
                            int(row[3])
                            try:
                                Product.objects.get(label=row[2])
                            except Product.DoesNotExist:
                                try:
                                    with transaction.atomic():
                                        new_prod = Product(
                                            name = row[0],
                                            description = row[1],
                                            label = row[2],
                                            reorder_level = row[3],
                                            order_quantity = row[4],
                                            order_unit_description = row[5],
                                            minimum_order_wait_duration = row[6],
                                            balance = row[7]
                                        )
                                        new_prod.save()
                                        new_stock = ProductStock(
                                            branch = branch,
                                            product = new_prod,
                                            quantity = row[7],
                                            unit_price = row[8],
                                            balance = row[7],
                                            ref_code = row[2],
                                            comment = 'Initial Database Upload'
                                        )
                                        new_stock.save()
                                    object_list.append(new_prod.name)
                                except:
                                    pass
                        except:
                            pass
                    context = {
                        'form': form,
                        'object_list': object_list,
                        }
                    return render(request, 'schedule/ctrl_importdb.html', context)
        else:
            context = {
                'form': form,
                }
            return render(request, 'schedule/ctrl_importdb.html', context)
    context = {
        'form': form,
        }
    return render(request, 'schedule/ctrl_importdb.html', context)


@login_required
def import_format(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/accounts/logout/')
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="import_format.csv"'
    writer = csv.writer(response)
    writer.writerow(['Product Name', 'Product Description(optional)', 'Product Code(Unique ID)', 
        'Re-order Level(the quantity where purchase order should be sent)', 
        'Order Quantity(the quantity that should be ordered)', 
        'Product Unit Title(e.g: Bag, Carton, Gallon, etc)', 
        'Order Wait Days(How many days before purchase order is resent'
        ' if merchant does not supply', 'Quantity Available', 'Unit Price'])
    return response


