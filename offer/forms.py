from django.forms import ModelForm

from offer.models import BrandOffer, CategoryOffer, ProductOffer


class BrandOfferForm(ModelForm):
    class Meta:
        model = BrandOffer
        fields = ["brand_name", "discount"]

    def __init__(self, *args, **kwargs):
        super(BrandOfferForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class CategoryOfferForm(ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ["category_name", "discount"]

    def __init__(self, *args, **kwargs):
        super(CategoryOfferForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class ProductOfferForm(ModelForm):
    class Meta:
        model = ProductOffer
        fields = ["product_name", "discount"]

    def __init__(self, *args, **kwargs):
        super(ProductOfferForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
