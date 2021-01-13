from django.contrib import admin
from .models import (MerchantReturn, MerchantSupply, StockBarcode, StockReceipt, 
StockReturned, ItemIssued, ItemRetrieved, DepartmentalProductReceipt, Product,
DepartmentalProductSupply, ProductStock, PurchaseOrder)
# Register your models here.

class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'unit_price', 'balance')
    list_filter = ('branch', 'date')
    search_fields = ('product__name', 'ref_code')


class MerchantReturnAdmin(admin.ModelAdmin):
    list_display = ('supply', 'quantity', 'ref_code', 'date')
    # list_filter = ('branch', 'date')
    # search_fields = ('product__name', 'ref_code')


admin.site.register(MerchantReturn, MerchantReturnAdmin)
admin.site.register(MerchantSupply)
admin.site.register(StockReturned)
admin.site.register(StockBarcode)
admin.site.register(StockReceipt)
admin.site.register(ItemRetrieved)
admin.site.register(ItemIssued)
admin.site.register(DepartmentalProductReceipt)
admin.site.register(DepartmentalProductSupply)
admin.site.register(ProductStock, ProductStockAdmin)
admin.site.register(Product)
admin.site.register(PurchaseOrder)
# admin.site.register(RecordBuffer)
# admin.site.register()
# admin.site.register()