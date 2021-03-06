# Generated by Django 3.1.1 on 2021-01-21 15:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userdata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileBank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('the_file', models.FileField(upload_to='')),
                ('file_name', models.CharField(max_length=250, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Business Name', max_length=250)),
                ('phone_number', models.CharField(max_length=13)),
                ('email_address', models.EmailField(max_length=254)),
                ('address', models.TextField()),
                ('liaison_officer', models.CharField(max_length=250)),
                ('liaison_officer_salutation', models.CharField(choices=[('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Miss', 'Miss')], max_length=10)),
                ('active', models.BooleanField(default=False)),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, null=True)),
                ('label', models.CharField(max_length=50, unique=True, verbose_name='Product Code')),
                ('reorder_level', models.PositiveIntegerField(help_text='Minimum Units Available Before Making Purchase Order')),
                ('order_quantity', models.PositiveIntegerField(default=5)),
                ('order_unit_description', models.CharField(help_text='e.g: Bag, Carton, Crate', max_length=50)),
                ('minimum_order_wait_duration', models.PositiveIntegerField(help_text='Within how many DAYS should delivery be made upon order?')),
                ('balance', models.PositiveIntegerField(help_text='total unit qty available irrespective of purchase date or price')),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockReceipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('merchant_ref_number', models.CharField(max_length=50, unique=True)),
                ('ref_code', models.CharField(max_length=10, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('comment', models.TextField(blank=True, null=True)),
                ('balance', models.PositiveIntegerField(help_text='Units left of the batch. Before issuing, it is equal to quantity')),
                ('confirm_entry', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('hide', models.BooleanField(default=False)),
                ('hide_reason', models.TextField(blank=True, null=True)),
                ('hidden_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stock_receipt_hidding_officer', to='userdata.officer')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.merchant')),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='userdata.officer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
            ],
        ),
        migrations.CreateModel(
            name='StockReturned',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('ref_code', models.CharField(max_length=12, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('confirm_entry', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('hide', models.BooleanField(default=False)),
                ('hide_reason', models.TextField(blank=True, null=True)),
                ('hidden_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stock_returned_hidding_officer', to='userdata.officer')),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='userdata.officer')),
                ('stock_receipt', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.stockreceipt')),
            ],
        ),
        migrations.CreateModel(
            name='StockBarcode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('barcode', models.ImageField(upload_to='inventory/%Y/%m')),
                ('code', models.CharField(max_length=15, unique=True)),
                ('creationdate', models.DateTimeField(auto_now_add=True)),
                ('product_expirydate', models.DateField()),
                ('scan_in_date', models.DateTimeField(blank=True, null=True)),
                ('scan_in_ref', models.CharField(max_length=15)),
                ('scanned_out', models.BooleanField(default=False)),
                ('scan_out_ref', models.CharField(max_length=15)),
                ('scan_out_date', models.DateTimeField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('fulfilled', models.BooleanField(default=False)),
                ('fulfilled_by', models.DateTimeField(blank=True, null=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.merchant')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('balance', models.PositiveIntegerField(help_text='Units left of the batch. Before issuing, it is equal to quantity')),
                ('ref_code', models.CharField(max_length=50, unique=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
            ],
        ),
        migrations.CreateModel(
            name='MerchantSupply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('ref_number', models.CharField(max_length=50)),
                ('ref_code', models.CharField(max_length=10, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('comment', models.TextField(blank=True, null=True)),
                ('confirm_entry', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('hide', models.BooleanField(default=False)),
                ('hide_reason', models.TextField(blank=True, null=True)),
                ('hidden_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='merchant_supply_hidding_officer', to='userdata.officer')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.merchant')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
                ('receiving_officer', models.ForeignKey(limit_choices_to={'department': 'dept_3'}, on_delete=django.db.models.deletion.PROTECT, to='userdata.officer')),
            ],
        ),
        migrations.CreateModel(
            name='MerchantReturn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref_code', models.CharField(max_length=12, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('supply_ref_number', models.CharField(max_length=50)),
                ('quantity', models.PositiveIntegerField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('confirm_entry', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('hide', models.BooleanField(default=False)),
                ('hide_reason', models.TextField(blank=True, null=True)),
                ('hidden_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='merchant_return_hidding_officer', to='userdata.officer')),
                ('returning_officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='userdata.officer')),
                ('supply', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.merchantsupply')),
            ],
        ),
        migrations.AddField(
            model_name='merchant',
            name='products',
            field=models.ManyToManyField(to='schedule.Product'),
        ),
        migrations.AddField(
            model_name='merchant',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ItemRetrieved',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('ref_code', models.CharField(max_length=15, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('returning_officer_department', models.CharField(choices=[('dept_1', 'control'), ('dept_2', 'kitchen'), ('dept_3', 'store')], max_length=50)),
                ('comment', models.TextField(blank=True, null=True)),
                ('quantity', models.PositiveIntegerField()),
                ('confirm_entry', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('hide', models.BooleanField(default=False)),
                ('hide_reason', models.TextField(blank=True, null=True)),
                ('hidden_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='item_retrieved_hidding_officer', to='userdata.officer')),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='item_retrieval_officer', to='userdata.officer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
                ('returning_officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='returning_officer', to='userdata.officer')),
            ],
        ),
        migrations.CreateModel(
            name='ItemIssued',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=11)),
                ('ref_code', models.CharField(max_length=11, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('receiving_officer_department', models.CharField(choices=[('dept_1', 'control'), ('dept_2', 'kitchen'), ('dept_3', 'store')], max_length=50)),
                ('comment', models.TextField(blank=True, null=True)),
                ('quantity', models.PositiveIntegerField()),
                ('confirm_entry', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('hide', models.BooleanField(default=False)),
                ('hide_reason', models.TextField(blank=True, null=True)),
                ('hidden_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='item_issued_hidding_officer', to='userdata.officer')),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='item_issue_officer', to='userdata.officer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
                ('receiving_officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='receiving_officer', to='userdata.officer')),
            ],
        ),
        migrations.CreateModel(
            name='DepartmentReturn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('quantity', models.PositiveIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('balance', models.PositiveIntegerField(help_text='Units left of the batch. Before issuing, it is equal to quantity')),
                ('ref_code', models.CharField(max_length=50, unique=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
            ],
        ),
        migrations.CreateModel(
            name='DepartmentalProductSupply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('ref_code', models.CharField(max_length=15, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('confirm_entry', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('hide', models.BooleanField(default=False)),
                ('hide_reason', models.TextField(blank=True, null=True)),
                ('department_officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='department_returning_officer', to='userdata.officer')),
                ('hidden_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dept_supply_hidding_officer', to='userdata.officer')),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='receiving_store_officer', to='userdata.officer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
            ],
        ),
        migrations.CreateModel(
            name='DepartmentalProductReceipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('ref_code', models.CharField(max_length=11, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('confirm_entry', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('hide', models.BooleanField(default=False)),
                ('hide_reason', models.TextField(blank=True, null=True)),
                ('department_officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='department_receiving_officer', to='userdata.officer')),
                ('hidden_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dept_receipt_hidding_officer', to='userdata.officer')),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='issuing_store_officer', to='userdata.officer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.product')),
            ],
        ),
    ]
