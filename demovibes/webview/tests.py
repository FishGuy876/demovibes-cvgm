from django.test import TestCase
from webview import models
from django.core.urlresolvers import reverse

# For documentation see:
#  Django specific : http://docs.djangoproject.com/en/1.1/topics/testing/#topics-testing
#  Python specific : http://docs.python.org/library/unittest.html

class BasicTest(TestCase):

    def setUp(self):
        """
        Run before each unit test, set up common values
        """
        self.user = models.User.objects.create_user('testuser', 'test@test.com', 'userpw')
        self.user.save()
        self.artist = models.Artist.objects.create(handle="Test artist")
        #self.song = models.Song.objects.create(title="Test song", file = "dummy/file")

    def tearDown(self):
        """
        Run afer each unit test, cleanup
        """
        self.user.delete()
        self.artist.delete()

    def test_login(self):
            upr = (
                ({ "username":"test", "password":"bla"}, 200, "I'm sorry, the username or password seem to be wrong."),
                ({ "username":"test", "ipassword":"bla"}, 200, "You need to supply a username and password"),
                ({ "iusername":"test", "password":"bla"}, 200, "You need to supply a username and password"),
                ({ "iusername":"test", "ipassword":"bla"}, 200, "You need to supply a username and password"),
                ({ "username":"", "password":"bla"}, 200, "You need to supply a username and password"),
                ({ "username":"asd", "password":""}, 200, "You need to supply a username and password"),
                ({ "username":"", "password":""}, 200, "You need to supply a username and password"),
            )
            for up, retcode, err in upr:
                r = self.client.post(reverse("dv-login"), up)
                self.assertContains(r, ">%s</p>" % err, 1, retcode)


    def login(self):
        r = self.client.post(reverse("dv-login"),
            {'username': "testuser", 'password': "userpw"})
        self.assertNotEqual(r.status_code, 200)

    def testPagesLoad(self):
        """
        Basic check if pages load or not
        """
        pages = ['dv-root', 'dv-songs', 'dv-platforms', "dv-streams",
                "dv-oneliner", "dv-recent", "dv-groups",
                "dv-artists", "dv-compilations", "dv-queue", "dv-labels",
                "dv-links", "dv-users_online"]
        pages = [reverse(a) for a in pages]

        pages.append(reverse("dv-artist", args = [self.artist.id]))
        pages.append(reverse("dv-profile", args = [self.user.username]))
        pages.append(reverse("dv-user-favs", args = [self.user.username]))

        restricted = ["dv-inbox", "dv-send_pm", "dv-my_profile", "dv-favorites",
                      "dv-createartist", "dv-creategroup", "dv-createlabel",
                      "dv-createlink"]
        restricted = [reverse(a) for a in restricted]
        restricted.append(reverse("dv-upload", args = [self.artist.id]))

        admin = ["dv-newlinks", "dv-newlabels", "dv-newgroups",
                "dv-newcompilations", "dv-newartists", "dv-uploads"]
        admin = [reverse(a) for a in admin]

        for page in pages:
            r = self.client.get(page)
            self.failUnlessEqual(r.status_code, 200, "Failed to load page %s" % page)

        for page in restricted + admin:
            r = self.client.get(page)
            self.assertRedirects(r, reverse("dv-login")+"?next=%s" % page)

        self.login()

        for page in pages + restricted:
            r = self.client.get(page)
            self.failUnlessEqual(r.status_code, 200, "Failed to load page %s" % page)

        for page in admin:
            r = self.client.get(page)
            self.assertRedirects(r, reverse("dv-login")+"?next=%s" % page)

    def testOneliner(self):
        """
        Test of oneliner
        """
        r = self.client.post(reverse("dv-oneliner_submit"), {'Line': "Test"})
        self.assertRedirects(r,
              reverse("dv-login")+"?next=%s" % reverse("dv-oneliner_submit"))

        r = self.client.post(reverse("dv-ax-oneliner_submit"),
          {'Line': "TestFailLine12345675"})
        self.assertContains(r, "NoAuth")
        self.assertEqual(models.Oneliner.objects.count(), 0)

        self.login()

        r = self.client.post(reverse("dv-oneliner_submit"), {'Line': "TestMoo"})
        self.assertEqual(models.Oneliner.objects.count(), 1)

        r = self.client.post(reverse("dv-oneliner_submit"), {'Line': ""})
        self.assertEqual(models.Oneliner.objects.count(), 1)

        r = self.client.get(reverse("dv-oneliner"))
        self.assertContains(r, "TestMoo")
        self.assertContains(r, "testuser")

        r = self.client.post(reverse("dv-ax-oneliner_submit"),
            {'Line': "TestLine12345678"})
        self.assertEqual(models.Oneliner.objects.count(), 2)

        r = self.client.post(reverse("dv-ax-oneliner_submit"), {'Line': ""})
        self.assertEqual(models.Oneliner.objects.count(), 2)

        r = self.client.get(reverse("dv-ax-oneliner"))
        self.assertContains(r, "TestLine12345678")
        self.assertContains(r, "TestMoo")
