from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_mode',
            field=models.CharField(
                choices=[('cod', 'Cash on Delivery')],
                default='cod',
                max_length=20
            ),
        ),
    ] 