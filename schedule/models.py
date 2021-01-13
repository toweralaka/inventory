from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from datetime import date, datetime, timedelta


from userdata.models import Merchant, BRANCHES, DEPARTMENT, Officer
from userdata.views import rannum, ranlet, send_email, send_html_email

User = get_user_model
# Create your models here.

def stock_comment(item, addition):
    if item is None:
        item = addition
    else:
        item = item + ", "+ addition
    return item


class Product(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    label = models.CharField(max_length=50, verbose_name="Product Code", unique=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT)
    reorder_level = models.PositiveIntegerField(
        help_text="Minimum Units Available Before Making Purchase Order"
        )
    order_quantity = models.PositiveIntegerField(default=5)
    order_unit_description = models.CharField(max_length=50, help_text="e.g: Bag, Carton, Crate")
    minimum_order_wait_duration = models.PositiveIntegerField(help_text="Within how many DAYS should delivery be made upon order?")
    balance = models.PositiveIntegerField(
        help_text="total unit qty available irrespective of purchase date or price"
        )

    def __str__(self):
        return f"{self.name}"

    def purchase_order(self):
        # send_email(request, msg, to, cc, subjt)
        n1 = "\n"
        plural = "s"
        if self.order_quantity <= 1:
            plural = ""
        msg = (f"Dear {self.merchant.the_merchant}, {n1}Kindly "
            f"supply us {self.order_quantity} "
            f"{self.order_unit_description}{plural} of {self.name}. {n1}"
            f"We would appreciate it if delivery is made "
            f"within {self.minimum_order_wait_duration} "
            f"days. {n1}Thank you.")
        to = self.merchant.email_address
        subjt = "PURCHASE ORDER"
        send_email(msg, to, subjt)
        new_order = PurchaseOrder(
            merchant=self.merchant,
            product=self,
        )
        new_order.save()

    def purchase_order_reminder(self):
        # send_email(request, msg, to, cc, subjt)
        n1 = "\n"
        plural = "s"
        if self.order_quantity <= 1:
            plural = ""
        msg = (f"Dear {self.merchant.the_merchant}, {n1}This is to "
            f"remind you of our order for {self.order_quantity} "
            f"{self.order_unit_description}{plural} of {self.name}. {n1}"
            f"We would appreciate it if delivery is made quickly."
            f"If delivery has already been made, please fill in delivery "
            f"information <a href='#'>here</a> "
            f"so that we can process payment. {n1}Thank you.")
        to = self.merchant.email_address
        subjt = "URGENT! PURCHASE ORDER"
        send_email(msg, to, subjt)
        

def purchase_order_receiver(sender, instance, *args, **kwargs):
    if instance.balance <= instance.reorder_level:
        try:
            the_order = PurchaseOrder.objects.get(product=instance, fulfilled=False)
            order_days = timezone.now() - the_order.date
            the_days = order_days.days
            if the_days >= instance.minimum_order_wait_duration:
                instance.purchase_order_reminder()
        except PurchaseOrder.DoesNotExist:
            instance.purchase_order()

post_save.connect(purchase_order_receiver, sender=Product)


class PurchaseOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    merchant = models.ForeignKey(Merchant, models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)
    fulfilled_by = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.product.name


class ProductStock(models.Model):
    branch = models.CharField(max_length=10, choices=BRANCHES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    balance = models.PositiveIntegerField(
        help_text="Units left of the batch. Before issuing, it is equal to quantity"
        )
    ref_code = models.CharField(max_length=50, unique=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name}"


class DepartmentReturn(models.Model):
    branch = models.CharField(max_length=10, choices=BRANCHES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    balance = models.PositiveIntegerField(
        help_text="Units left of the batch. Before issuing, it is equal to quantity"
        )
    ref_code = models.CharField(max_length=50, unique=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name}"


# Merchant  Supply
class MerchantSupply(models.Model):
    branch = models.CharField(max_length=10, choices=BRANCHES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    ref_number = models.CharField(max_length=50)
    ref_code = models.CharField(max_length=10, unique=True) #auto generate
    date = models.DateTimeField(auto_now_add=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT) #loggedin
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(null=True, blank=True)
    receiving_officer = models.ForeignKey(
        Officer, on_delete=models.PROTECT, 
        limit_choices_to={'department': 'dept_3'})
    confirm_entry = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.merchant} - {self.ref_number}"

    def is_entry_accepted(self):
        if entries_equal:
            return True
        else:
            return False

    def unconfirm_supply(self):
        # send_email(request, msg, to, cc, subjt)
        n1 = "\n"
        cc = "djaafolayan@gmail.com"
        plural = "s"
        the_link = "<a href='#'>here</a>"
        if self.quantity <= 1:
            plural = ""
        html_msg = (f"Dear {self.receiving_officer.name}, <br />In our supply "
            f"with reference number {self.ref_number}, we "
            f"supplied {self.quantity} "
            f"{self.product.order_unit_description}{plural} of "
            f"{self.product.name}. <br />Please crosscheck your records "
            f"and update the supply form {the_link} "
            f". <br />Thank you."
            f"{self.merchant.liaison_officer}({self.merchant.name})")
        msg = (f"Dear {self.receiving_officer.name}, {n1}In our supply "
            f"with reference number {self.ref_number}, we "
            f"supplied {self.quantity} "
            f"{self.product.order_unit_description}{plural} of "
            f"{self.product.name}. {n1}. Please crosscheck your records "
            f"and update the supply form at https:// "
            f". {n1}Thank you."
            f"{self.merchant.liaison_officer}({self.merchant.name})")
        to = self.receiving_officer.email_address
        subjt = "URGENT! UPDATE SUPPLY INFORMATION!"
        send_html_email(msg, html_msg, to, subjt, cc)


def verify_supply_receiver(sender, instance, *args, **kwargs):
    if not instance.verified:
        if instance.confirm_entry:
            stock = StockReceipt.objects.get(ref_code=instance.ref_code)
            if instance.quantity == stock.quantity:
                # instance.verified = True
                stock.verified = True
                stock.save()
                newstock = ProductStock(
                    branch=instance.branch,
                    product=instance.product,
                    unit_price=instance.unit_price,
                    quantity=instance.quantity,
                    date=stock.date,
                    balance=instance.quantity,
                    ref_code=instance.ref_code
                )
                newstock.save()
            else:
                instance.unconfirm_supply()

post_save.connect(verify_supply_receiver, sender=MerchantSupply)


#Store Receipt
class StockReceipt(models.Model):#(on verified, update Stock record)
    branch = models.CharField(max_length=10, choices=BRANCHES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    merchant_ref_number = models.CharField(max_length=50, unique=True)
    ref_code = models.CharField(max_length=10, unique=True) #auto generate, same as merchant supply
    merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT) #(not necessary? why?)
    # scan_in = models.ForeignKey(ScanIn, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()#(increment as product is scanned in)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)#(to show value of stock)
    officer = models.ForeignKey(Officer, on_delete=models.PROTECT)#(loggedin)
    comment = models.TextField(null=True, blank=True)
    balance = models.PositiveIntegerField(
        help_text="Units left of the batch. Before issuing, it is equal to quantity"
        )
    confirm_entry = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.merchant_ref_number

    def is_new_supply(self):
        try:
            MerchantSupply.objects.get(ref_code=self.ref_code)
            return False
        except MerchantSupply.DoesNotExist:
            return True


    def supply_alert(self):
        n1 = "\n"
        plural = "s"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.merchant.the_merchant}, {n1}We just received {self.quantity} "
            f"{self.product.order_unit_description}{plural} of {self.product.name}. "
            f"{n1}Please confirm our receipt <a href='#'>here</a> "
            f"so that payment can be processed. {n1}Thank you.{n1}"
            f"{self.officer.name}(BSL)")
        to = self.merchant.email_address
        subjt = "URGENT! CONFIRM SUPPLY"
        send_email(msg, to, subjt)

    def officer_default(self):
        n1 = "\n"
        plural = "s"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.merchant.the_merchant}, {n1}You have not confirmed "
            f"the supply of {self.quantity} "
            f"{self.product.order_unit_description}{plural} of {self.product.name}. "
            f"I am assuming that the goods were supplied for free. "
            f"{n1}We, therefore do not owe you concerning the supply"
            f"{n1}Thank you for your benevolence.{n1}"
            f"{self.officer.name}(BSL)")
        to = self.merchant.email_address
        subjt = "WE DO NOT OWE YOU!"
        send_email(msg, to, subjt)


def set_ref_code_receiver(sender, instance, *args, **kwargs):
    supply = instance
    if not supply.ref_code:
        right_now = datetime.now()
        code = str(right_now.strftime("%Y%m%d")) + str(rannum(1)) + str(ranlet(1))
        supply.ref_code = code
pre_save.connect(set_ref_code_receiver, sender=StockReceipt)

def check_supply_entry_receiver(sender, instance, *args, **kwargs):
    try:
        d_supply = MerchantSupply.objects.get(ref_code=supply.ref_code)
        if supply.verified:
            d_supply.verified = True
            d_supply.save()
        else:
            d_supply.confirm_entry = False
            d_supply.save()
            supply.supply_alert()
    except MerchantSupply.DoesNotExist:
        new_stock = MerchantSupply(
            merchant=supply.merchant,
            product=supply.product,
            receiving_officer=supply.officer,
            branch=supply.branch,
            ref_code=supply.ref_code,
            quantity=supply.quantity,
            unit_price=supply.unit_price,
            ref_number=supply.merchant_ref_number,
            amount=supply.quantity * supply.unit_price,
            tax=0.0,
            total_amount=supply.quantity * supply.unit_price
        )
        new_stock.save()
        supply.supply_alert()

post_save.connect(check_supply_entry_receiver, sender=StockReceipt)


#Merchant Record Of Returns
class MerchantReturn(models.Model):
    supply = models.ForeignKey(
        MerchantSupply, on_delete=models.PROTECT, 
        )
    ref_code = models.CharField(max_length=12, unique=True) #auto generate
    date = models.DateTimeField(auto_now_add=True)
    supply_ref_number = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    comment = models.TextField(null=True, blank=True)
    returning_officer = models.ForeignKey(Officer, on_delete=models.PROTECT)
    confirm_entry = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.supply.ref_number

    def unconfirm_return(self):
        n1 = "\n"
        plural = "s"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.returning_officer}, {n1}In your returns we "
            f"received {self.quantity} "
            f"{self.supply.product.order_unit_description}{plural} of "
            f"{self.supply.product.name}. {n1}. Please crosscheck your records "
            f"and update the returns form <a href='#'>here</a> "
            f". {n1}Thank you.{n1}"
            f"{self.supply.merchant.liaison_officer}({self.supply.merchant.name})")
        to = self.returning_officer.email_address
        subjt = "URGENT! UPDATE RETURNS INFORMATION!"
        send_email(msg, to, subjt)


def verify_returns_receiver(sender, instance, *args, **kwargs):
    if not instance.verified:
        if instance.confirm_entry:
            returns = StockReturned.objects.get(ref_code=instance.ref_code)
            if instance.quantity == returns.quantity:
                returns.verified = True
                returns.save()
                d_stock = ProductStock.objects.get(ref_code=instance.supply.ref_code)
                d_stock.quantity -= returns.quantity
                d_stock.balance -= returns.quantity
                if d_stock.comment is None:
                    d_stock.comment = returns.ref_code
                else:
                    d_stock.comment = d_stock.comment + ", " + returns.ref_code
                d_stock.save()
            else:
                instance.unconfirm_return()

post_save.connect(verify_returns_receiver, sender=MerchantReturn)


#Store Returns To Merchant
class StockReturned(models.Model):#(on verify, update stock record)
    stock_receipt = models.ForeignKey(StockReceipt, on_delete=models.PROTECT)
    branch = models.CharField(max_length=10, choices=BRANCHES)
    ref_code = models.CharField(
        max_length=12, unique=True) #auto generate, same as merchant return
    # scan_out = models.ForeignKey(ScanOut, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()#(increment as product is scanned out)
    comment = models.TextField(null=True, blank=True)
    officer = models.ForeignKey(Officer, on_delete=models.PROTECT)#(loggedin)
    confirm_entry = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.ref_code

    def is_new_return(self):
        try:
            MerchantReturn.objects.get(ref_code=self.ref_code)
            return False
        except MerchantReturn.DoesNotExist:
            return True

    def return_alert(self):
        n1 = "\n"
        plural = "s"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.stock_receipt.merchant.the_merchant}, {n1}"
            f"I just returned {self.quantity} "
            f"{self.stock_receipt.product.order_unit_description}{plural} of {self.stock_receipt.product.name}. "
            f"{n1}Due to:{n1} {self.comment}."
            f"{n1}Please confirm the returns <a href='#'>here</a> "
            f"so that your payment can be processed. {n1}Thank you.{n1}"
            f"{self.officer.name}(BSL)")
        to = self.stock_receipt.merchant.email_address
        subjt = "URGENT! CONFIRM RETURNS"
        send_email(msg, to, subjt)

    def merchant_default(self):
        n1 = "\n"
        plural = "s"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.stock_receipt.merchant.the_merchant}, "
            f"{n1}You have not confirmed the returns of {self.quantity} "
            f"{self.stock_receipt.product.order_unit_description}{plural}"
            f" of {self.stock_receipt.product.name}. "
            f"I am assuming you accepted the goods for your personal use. "
            f"{n1}Kindly make payment of "
            f"{self.quantity * self.stock_receipt.unit_price} "
            f"within the next 5 work days. {n1}Thank you.{n1}"
            f"{self.officer.name}(BSL)")
        to = self.stock_receipt.merchant.email_address
        subjt = "YOU OWE US!"
        send_email(msg, to, subjt)


def set_return_ref_code_receiver(sender, instance, *args, **kwargs):
    if not instance.ref_code:
        right_now = datetime.now()
        code = str(right_now.strftime("%Y%m%d")) + str(rannum(2)) + str(ranlet(2))
        instance.ref_code = code
pre_save.connect(set_return_ref_code_receiver, sender=StockReturned)

def set_equal_return_receiver(sender, instance, *args, **kwargs):
    try:
        d_return = MerchantReturn.objects.get(ref_code=instance.ref_code)
        if instance.verified:
            d_return.verified = True
            d_return.save()
        elif instance.quantity == d_return.quantity:
            d_return.confirm_entry = True
            d_return.save()
        else:
            d_return.confirm_entry = False
            d_return.save()
            instance.return_alert()
    except MerchantReturn.DoesNotExist:
        new_returns = MerchantReturn(
            supply = MerchantSupply.objects.get(
                ref_code=instance.stock_receipt.ref_code),
            returning_officer=instance.officer,
            ref_code=instance.ref_code,
            quantity=instance.quantity,
        )
        new_returns.save()
        instance.return_alert()

post_save.connect(set_equal_return_receiver, sender=StockReturned)


#Store keeper entries with other departments
class ItemIssued(models.Model):#(on verified, record Stock)
    branch = models.CharField(max_length=11, choices=BRANCHES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    ref_code = models.CharField(
        max_length=11, unique=True) #auto generate, same as dept receipt
    officer = models.ForeignKey(
        Officer, on_delete=models.PROTECT, related_name="item_issue_officer")#(loggedin)
    date = models.DateTimeField(auto_now_add=True)
    # scan_out = models.ForeignKey(ScanOut, on_delete=models.PROTECT)
    receiving_officer = models.ForeignKey(
        Officer, on_delete=models.PROTECT, related_name="receiving_officer")
    receiving_officer_department = models.CharField(
        max_length=50, choices=DEPARTMENT)
    comment = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField() #(increment as product is scanned out)
    confirm_entry = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)# true when both accounts align

    def __str__(self):            
        return self.ref_code
    
    def is_new_issue(self):
        try:
            DepartmentalProductReceipt.objects.get(ref_code=self.ref_code)
            return False
        except DepartmentalProductReceipt.DoesNotExist:
            return True

    # def is_verified()
    def is_entries_same(self):
        dept_rec = DepartmentalProductReceipt.objects.get(ref_code=self.ref_code)
        if self.quantity == dept_rec.quantity:
            return True
        else:
            return False

    def get_issue_stock_list(self):
        qty = 0
        stock_list = []
        for stock in ProductStock.objects.filter(
            product=self.product, balance__gt=0).order_by('date'):
            if qty < self.quantity:
                qty += stock.balance
                stock_list.append(stock)
            else:
                break
        return stock_list

    def both_entries_confirmed(self):
        dept = DepartmentalProductReceipt.objects.get(ref_code=self.ref_code)
        if self.confirm_entry and dept.confirm_entry:
            return True
        else:
            return False

    def get_unit_price(self):
        return self.get_issue_stock_list()[0].unit_price

    def issue_alert(self):
        n1 = "\n"
        plural = "s"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.receiving_officer.name}, {n1}"
            f"I just issued you {self.quantity} "
            f"{self.product.order_unit_description}{plural} of {self.product.name}. "
            f"{n1}Please confirm the transaction <a href='#'>here</a> "
            f". {n1}Thank you.{n1}{self.officer.name}({self.officer.department})")
        to = self.receiving_officer.email_address
        subjt = "URGENT! CONFIRM RECEIPT!"
        send_email(msg, to, subjt)

    def department_default(self):
        n1 = "\n"
        unit_price = self.product.get_unit_price()
        plural = "s"
        cc = "djaafolayan@gmail.com"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.receiving_officer.name}, {n1}You have not confirmed "
            f"the {self.quantity} "
            f"{self.product.order_unit_description}{plural} of {self.product.name} "
            f"I issued. I am assuming you accepted the goods for your personal use. "
            f"{n1}Kindly make payment of "
            f"{self.quantity * unit_price} "
            f"within the next 5 work days. {n1}Thank you.{n1}"
            f"{self.officer.name}({self.officer.department})")
        to = self.receiving_officer.email_address
        subjt = "YOU OWE US!"
        send_email(msg, to, subjt, cc)


def set_issue_ref_code_receiver(sender, instance, *args, **kwargs):
    if not instance.ref_code:
        right_now = datetime.now()
        code = str(right_now.strftime("%Y%m%d")) + str(rannum(2)) + str(ranlet(1))
        instance.ref_code = code
    elif instance.is_new_issue():
        pass
    elif instance.both_entries_confirmed():
        if instance.is_entries_same():
            instance.verified = True

pre_save.connect(set_issue_ref_code_receiver, sender=ItemIssued)

def adjust_dept_receipt_receiver(sender, instance, *args, **kwargs):
    if instance.is_new_issue():
        d_issue = DepartmentalProductReceipt(
            officer=instance.officer,
            product=instance.product,
            department_officer=instance.receiving_officer,
            branch=instance.branch,
            ref_code=instance.ref_code,
            quantity=instance.quantity,
        )
        d_issue.save()
        instance.issue_alert()
    else:
        old_issue = DepartmentalProductReceipt.objects.get(ref_code=instance.ref_code)
        if instance.is_entries_same():
            old_issue.verified = True
            old_issue.save()
        else:
            old_issue.confirm_entry = False
            old_issue.save()
            instance.issue_alert()

post_save.connect(adjust_dept_receipt_receiver, sender=ItemIssued)


class DepartmentalProductReceipt(models.Model):
    branch = models.CharField(max_length=10, choices=BRANCHES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    ref_code = models.CharField(max_length=11, unique=True) #auto generate, same as item issued
    officer = models.ForeignKey(
        Officer, on_delete=models.PROTECT, related_name="issuing_store_officer")#(loggedin)
    date = models.DateTimeField(auto_now_add=True)
    department_officer = models.ForeignKey(
        Officer, on_delete=models.PROTECT, related_name="department_receiving_officer")
    quantity = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    confirm_entry = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.ref_code

    def is_stock_entered(self):
        try:
            ProductStock.objects.get(ref_code=self.ref_code)
            return True
        except ProductStock.DoesNotExist:
            return False

    def issue_from_stock(self):#, refcode):
        store_issue = ItemIssued.objects.get(ref_code=self.ref_code)
        d_bal = self.quantity
        for d_stock in store_issue.get_issue_stock_list():
            if d_bal > d_stock.balance:
                d_bal -= d_stock.balance
                d_stock.balance=0
                stock_comment(d_stock.comment, self.ref_code)
                d_stock.save()
            else:
                d_stock.balance -= d_bal
                d_bal = 0
                stock_comment(d_stock.comment, self.ref_code)
                d_stock.save()   


    def unconfirm_dept_receipt(self):
        # send_email(request, msg, to, cc, subjt)
        n1 = "\n"
        cc = "djaafolayan@gmail.com"
        plural = "s"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.officer.name}, {n1}In your issue "
            f"with reference number {self.ref_code}, I "
            f"received {self.quantity} "
            f"{self.product.order_unit_description}{plural} of "
            f"{self.product.name}. {n1}. Please crosscheck your records "
            f"and update the issue form <a href='#'>here</a> "
            f". {n1}Thank you."
            f"{self.officer.name}({self.officer.department})")
        to = self.officer.email_address
        subjt = "URGENT! UPDATE ISSUE INFORMATION!"
        send_email(msg, to, subjt, cc)

def verify_issue_receiver(sender, instance, *args, **kwargs):
    if not instance.verified:
        if instance.confirm_entry:
            issue = ItemIssued.objects.get(ref_code=instance.ref_code)
            if issue.is_entries_same():
                issue.verified = True
                issue.save()

post_save.connect(verify_issue_receiver, sender=DepartmentalProductReceipt)

def stock_entry_receiver(sender, instance, *args, **kwargs):
    if instance.verified:
        if not instance.is_stock_entered():
            instance.issue_from_stock()
    else:
        issue = ItemIssued.objects.get(ref_code=instance.ref_code)
        if issue.is_entries_same():
            issue.verified = True
            issue.save()

post_save.connect(stock_entry_receiver, sender=DepartmentalProductReceipt)


class ItemRetrieved(models.Model):#(on verify, update stock record)
    branch = models.CharField(max_length=10, choices=BRANCHES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    ref_code = models.CharField(max_length=15, unique=True) #auto generate, same as merchant supply
    officer = models.ForeignKey(
        Officer, on_delete=models.PROTECT, related_name="item_retrieval_officer")#(loggedin)
    date = models.DateTimeField(auto_now_add=True)
    # scan_out = models.ForeignKey(ScanOut, on_delete=models.PROTECT)
    returning_officer = models.ForeignKey(
        Officer, on_delete=models.PROTECT, related_name="returning_officer")
    returning_officer_department = models.CharField(
        max_length=50, choices=DEPARTMENT)
    comment = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField() #(increment as product is scanned in)
    confirm_entry = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):            
        return self.ref_code
    
    def is_new_return(self):
        try:
            DepartmentalProductSupply.objects.get(ref_code=self.ref_code)
            return False
        except DepartmentalProductSupply.DoesNotExist:
            return True

    # def is_verified()
    def is_entries_same(self):
        dept_ret = DepartmentalProductSupply.objects.get(ref_code=self.ref_code)
        if self.quantity == dept_ret.quantity:
            return True
        else:
            return False

    # def get_return_stock_list(self):
    #     qty = 0
    #     stock_list = []
    #     for stock in ProductStock.objects.filter(
    #         product=self.product, balance__gt=0).order_by('date'):
    #         if qty < self.quantity:
    #             qty += stock.balance
    #             stock_list.append(stock)
    #         else:
    #             break
    #     return stock_list

    def both_entries_confirmed(self):
        dept = DepartmentalProductSupply.objects.get(ref_code=self.ref_code)
        if self.confirm_entry and dept.confirm_entry:
            return True
        else:
            return False

    def receipt_alert(self):
        n1 = "\n"
        plural = "s"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.returning_officer.name}, {n1}"
            f"I just received {self.quantity} "
            f"{self.product.order_unit_description}{plural} of {self.product.name}. "
            f"{n1}Please confirm the transaction <a href='#'>here</a> "
            f". {n1}Thank you.{n1}{self.officer.name}({self.officer.department})")
        to = self.returning_officer.email_address
        subjt = "URGENT! CONFIRM RECEIPT!"
        send_email(msg, to, subjt)

    def department_default(self):
        n1 = "\n"
        plural = "s"
        cc = "djaafolayan@gmail.com"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.returning_officer.name}, {n1}You have not confirmed "
            f"the {self.quantity} "
            f"{self.product.order_unit_description}{plural} of {self.product.name} "
            f"you delivered. I am assuming that you did not return any item and the "
            f"transaction was entered in error.{n1}"
            f"{n1}Thank you for your benevolence.{n1}"
            f"{self.officer.name}({self.officer.department})")
        to = self.returning_officer.email_address
        subjt = "THANK YOU FOR THE GIFT!"
        send_email(msg, to, subjt, cc)


def set_receive_ref_code_receiver(sender, instance, *args, **kwargs):
    if not instance.ref_code:
        right_now = datetime.now()
        code = str(right_now.strftime("%Y%m%d")) + str(rannum(3)) + str(ranlet(4))
        instance.ref_code = code
    elif instance.is_new_return():
        pass
    elif instance.both_entries_confirmed():
        if instance.is_entries_same():
            instance.verified = True

pre_save.connect(set_receive_ref_code_receiver, sender=ItemRetrieved)

def adjust_dept_return_receiver(sender, instance, *args, **kwargs):
    if instance.is_new_return():
        d_return = DepartmentalProductSupply(
            officer=instance.officer,
            product=instance.product,
            department_officer=instance.receiving_officer,
            branch=instance.branch,
            ref_code=instance.ref_code,
            quantity=instance.quantity,
        )
        d_return.save()
        instance.receipt_alert()
    else:
        old_return = DepartmentalProductSupply.objects.get(ref_code=instance.ref_code)
        if instance.is_entries_same():
            old_return.verified = True
            old_return.save()
        else:
            old_return.confirm_entry = False
            old_return.save()
            instance.receipt_alert()

post_save.connect(adjust_dept_return_receiver, sender=ItemRetrieved)


class DepartmentalProductSupply(models.Model):
    branch = models.CharField(max_length=10, choices=BRANCHES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    ref_code = models.CharField(max_length=15, unique=True) #auto generate, same as item retrieved
    officer = models.ForeignKey(
        Officer, on_delete=models.PROTECT, related_name="receiving_store_officer")#(loggedin)
    date = models.DateTimeField(auto_now_add=True)
    department_officer = models.ForeignKey(
        Officer, on_delete=models.PROTECT, related_name="department_returning_officer")
    quantity = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    confirm_entry = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.ref_code

    def is_stock_entered(self):
        try:
            DepartmentReturn.objects.get(ref_code=self.ref_code)
            return True
        except DepartmentReturn.DoesNotExist:
            return False

    def return_to_stock(self):
        new_returns = DepartmentReturn(
            branch = self.branch,
            product = self.product,
            quantity = self.quantity,
            balance = self.quantity,
            ref_code = self.ref_code)
        new_returns.save()

    def unconfirm_dept_return(self):
        # send_email(request, msg, to, cc, subjt)
        n1 = "\n"
        cc = "djaafolayan@gmail.com"
        plural = "s"
        if self.quantity <= 1:
            plural = ""
        msg = (f"Dear {self.officer.name}, {n1}In the returns "
            f"with reference number {self.ref_code}, I "
            f"returned {self.quantity} "
            f"{self.product.order_unit_description}{plural} of "
            f"{self.product.name}. {n1}. Please crosscheck your records "
            f"and update the return form <a href='#'>here</a> "
            f". {n1}Thank you."
            f"{self.department_officer.name}({self.department_officer.department})")
        to = self.officer.email_address
        subjt = "URGENT! UPDATE ISSUE INFORMATION!"
        send_email(msg, to, subjt, cc)

def verify_return_receiver(sender, instance, *args, **kwargs):
    if not instance.verified:
        if instance.confirm_entry:
            issue = ItemRetrieved.objects.get(ref_code=instance.ref_code)
            if issue.is_entries_same():
                issue.verified = True
                issue.save()

post_save.connect(verify_return_receiver, sender=DepartmentalProductSupply)

def return_entry_receiver(sender, instance, *args, **kwargs):
    if instance.verified:
        if not instance.is_stock_entered():
            instance.return_to_stock()
    else:
        issue = ItemRetrieved.objects.get(ref_code=instance.ref_code)
        if issue.is_entries_same():
            issue.verified = True
            issue.save()

post_save.connect(return_entry_receiver, sender=DepartmentalProductSupply)


#To track items first in and ensure they are first out
class StockBarcode(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    branch = models.CharField(max_length=10, choices=BRANCHES)
    barcode = models.ImageField(upload_to='inventory/%Y/%m')
    code = models.CharField(max_length=15, unique=True)#(unique, autocreate)
    creationdate = models.DateTimeField(auto_now_add=True)
    product_expirydate = models.DateField()#(alert for usage a month before expiration)
    scan_in_date = models.DateTimeField(blank=True, null=True)
    scan_in_ref = models.CharField(max_length=15)
    scanned_out = models.BooleanField(default=False)#(boolean...if true, clear from db after 3 month)
    scan_out_ref = models.CharField(max_length=15)
    scan_out_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.code


# class StockReceipt(models.Model):
#     item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
#     quantity = models.PositiveIntegerField()
#     merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT)
#     updated = models.BooleanField()
#     entry_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.item.item_name}"


# StockIn(on save, record Stock)
# branch(ogab, ikeja, ikotun)
# product
# date
# price
# merchant(not necessary? why?)
# quantity(increment as product is scanned in)
# balance
# amount(to show value of stock)
# officer(loggedin)


"""
NOTES
#if one-sided transaction occurs, alert both parties and control

#if merchant does not fill online form, merchant does not get paid

# when transactions are unverified send " you owe NGN 1000" to the defaulting party
"""



# #temporary holder for scans in then total transfered to StockReceipt or ItemReturned
# class ScanIn(models.Model):
#     branch = models.CharField(max_length=10, choices=BRANCHES)
#     product = models.ForeignKey(Product, on_delete=models.PROTECT)
#     ref_code = models.CharField(max_length=10, unique=True) #auto generate, same as merchant supply
#     officer = models.ForeignKey(Officer, on_delete=models.PROTECT)#(loggedin)
#     quantity = models.PositiveIntegerField()#(increment as product is scanned in)

#     def __str__(self):
#         return self.ref_code


# #temporary holder for scans out then total transfered to StockReturned or ItemIssued
# class ScanOut(models.Model):
#     branch = models.CharField(max_length=10, choices=BRANCHES)
#     product = models.ForeignKey(Product, on_delete=models.PROTECT)
#     ref_code = models.CharField(max_length=10, unique=True) #auto generate, same as merchant supply
#     officer = models.ForeignKey(Officer, on_delete=models.PROTECT)#(loggedin)
#     quantity = models.PositiveIntegerField()#(increment as product is scanned in)



