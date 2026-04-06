import pytest
from django.contrib.auth.models import User

from apps.clients.models import Client, FavoriteMaster
from apps.staff.models import Master


@pytest.mark.django_db
class TestClientModel:
    def test_str(self):
        client = Client.objects.create(phone='+79001111111')
        assert str(client) == '+79001111111'

    def test_auto_referral_code(self):
        client = Client.objects.create(phone='+79002222222')
        assert client.referral_code is not None
        assert len(client.referral_code) == 10

    def test_referral_code_unique(self):
        codes = set()
        for i in range(20):
            c = Client.objects.create(phone=f'+79003333{i:04d}')
            codes.add(c.referral_code)
        assert len(codes) == 20

    def test_bonus_balance_default(self):
        client = Client.objects.create(phone='+79004444444')
        assert client.bonus_balance == 0

    def test_one_to_one_user(self):
        user = User.objects.create_user(username='clientuser', password='pass')
        client = Client.objects.create(user=user, phone='+79005555555')
        assert user.client_profile == client

    def test_referral_relationship(self):
        referrer = Client.objects.create(phone='+79006666666')
        referred = Client.objects.create(phone='+79007777777', referred_by=referrer)
        assert referred.referred_by == referrer
        assert referrer.referred_clients.filter(id=referred.id).exists()

    def test_user_can_be_null(self):
        client = Client.objects.create(phone='+79008888888')
        assert client.user is None

    def test_phone_unique(self):
        Client.objects.create(phone='+79009999999')
        with pytest.raises(Exception):
            Client.objects.create(phone='+79009999999')


@pytest.mark.django_db
class TestFavoriteMasterModel:
    def test_str(self):
        user = User.objects.create_user(username='fav_client')
        client = Client.objects.create(user=user, phone='+79001111111')
        master_user = User.objects.create_user(username='fav_master')
        master = Master.objects.create(user=master_user, phone='+79002222222')
        fav = FavoriteMaster.objects.create(client=client, master=master)
        assert str(fav) == f'{client} — {master}'

    def test_unique_together(self):
        user = User.objects.create_user(username='fav_client2')
        client = Client.objects.create(user=user, phone='+79003333333')
        master_user = User.objects.create_user(username='fav_master2')
        master = Master.objects.create(user=master_user, phone='+79004444444')
        FavoriteMaster.objects.create(client=client, master=master)
        with pytest.raises(Exception):
            FavoriteMaster.objects.create(client=client, master=master)

    def test_cascade_delete_client(self):
        user = User.objects.create_user(username='fav_client3')
        client = Client.objects.create(user=user, phone='+79005555555')
        master_user = User.objects.create_user(username='fav_master3')
        master = Master.objects.create(user=master_user, phone='+79006666666')
        fav = FavoriteMaster.objects.create(client=client, master=master)
        client.delete()
        assert not FavoriteMaster.objects.filter(id=fav.id).exists()

    def test_cascade_delete_master(self):
        user = User.objects.create_user(username='fav_client4')
        client = Client.objects.create(user=user, phone='+79007777777')
        master_user = User.objects.create_user(username='fav_master4')
        master = Master.objects.create(user=master_user, phone='+79008888888')
        fav = FavoriteMaster.objects.create(client=client, master=master)
        master.delete()
        assert not FavoriteMaster.objects.filter(id=fav.id).exists()
