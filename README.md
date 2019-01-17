Example Monzo Transaction Receipts API Client
=========

The Transaction Receipts API is a new, experimental API for you to attach or read detailed receipt data of Monzo transactions. Whether it is using your card at a shop, or sending someone money for a favour, keeping all your spending data in one place has never been easier! With this API, you can decide how to source or generate the receipt.

![Transaction Receipt View](https://user-images.githubusercontent.com/42541688/51318101-42637c00-1a51-11e9-98eb-f73cacff9bdc.jpg)

## Getting Started
You need a Monzo account to register and manage your OAuth2 API clients. If you don't yet have a Monzo account, you can [open an account](https://monzo.com) on your phone now -- it takes no more than a few minutes with an ID on hand. Search for `Monzo` in App Store and Play Store.

To register your API client, head to [developers.monzo.com](http://developers.monzo.com), and select `Sign in with your Monzo account`. You'll receive an email sign in link, as the Developers Portal itself is an OAuth application. Once you've logged in, go to `Client`, and click on `New OAuth Client`. You'll need to provide the following information to register a client:

* **Name**: The name of your application. Your users see it when redirected to auth.monzo.com to Sign in.
* **Logo URL**: A link to the logo image of your application, although this is not currently displayed.
* **Redirect URLs**: The callback URLs to your application. In this example application, we don't actually handle a callback, but only parse the temporary auth code returned. Therefore we use one fake local URL of `http://127.0.0.1:21234/`. A real application will ideally handle auth flows automatically, and an internet-accessible callback endpoint will be needed here instead.
* **Description**: A short description on the purpose of your application. Feel free to put anything here.
* **Confidentiality**: A confidential API client will keep the OAuth2 secret from your user, and hence will be allowed to [refresh](https://docs.monzo.com/#refreshing-access) access tokens with a refresh token. While a non-confidential client may expose its OAuth2 secrets to the client, such as embedded in the JavaScript of a web application. As our simple client will be kept locally for now, feel free to set it as `Confidential` here.

Once you have registered your API client, you will have received a Client ID and a Client Secret. The next step is to clone this repository:
```
git clone https://github.com/monzo/reference-receipts-app.git
cd reference-receipts-app
```

Now we need to configure the client:
```
cp config-example.py config.py
```
And edit `config.py` with your favourite editor to set `MONZO_CLIENT_ID` and `MONZO_CLIENT_SECRET`. 

The example client is written in Python3. You will ideally need Python3.6 and `pip`. We need to install some dependencies, preferably in a virtual environment. We will be using `virtualenv` in this example:
```
virtualenv env -p python3
source env/bin/activate
pip install -r requirements.txt
```

Your client should now be ready to use. To see a quick demo of this example client, simply do:
```
python main.py
```
And follow the authentication flow as prompted.

Our client will automatically add some fabricated receipt data into your most recent Monzo transaction, which you can view in your Monzo app by clicking on that transaction. It does not affect any other parts of your account, so no need to worry about the data!

To see how the API calls worked underneath, the code should hopefully be fairly straightforward.

## Extending the Application
This example API client is very basic: it does not source receipt data from elsewhere, and does not run a server to accept webhook calls from Monzo and thus adding receipts to new transactions as they pop up. This is where you step in to make the magic happen! 

If you are working with this at a Monzo-sponsored hack day, feel free to ask one of your friendly Monzo mentors at any time to give a hand!
