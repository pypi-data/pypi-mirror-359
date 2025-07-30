# AA Fleet Finder<a name="aa-fleet-finder"></a>
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)
Control access to your fleets through Alliance Auth.

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Installation](#installation)
  - [Step 1: Install the Package](#step-1-install-the-package)
  - [Step 2: Configure Alliance Auth](#step-2-configure-alliance-auth)
  - [Step 3: Finalizing the Installation](#step-3-finalizing-the-installation)
  - [Step 4: Setup Permissions](#step-4-setup-permissions)

<!-- mdformat-toc end -->

______________________________________________________________________

## Installation<a name="installation"></a>

> [!NOTE]
>
> **AA Fleet Finder >= 2.0.0 needs at least Alliance Auth v4.0.0!**
>
> Please make sure to update your Alliance Auth instance _before_ you install this
> module or update to the latest version, otherwise an update to Alliance Auth will
> be pulled in unsupervised.
>
> 💡 AA Greenlight requires both `aa-fittings` and `eveuniverse` to function properly.


### Step 1: Install the Package<a name="step-1-install-the-package"></a>

Make sure you're in the virtual environment (venv) of your Alliance Auth installation Then install the latest release directly from PyPi.

```shell
pip install aa-greenlight
```

### Step 2: Configure Alliance Auth<a name="step-2-configure-alliance-auth"></a>

This is fairly simple, just add the following to the `INSTALLED_APPS` of your `local.py`

Configure your AA settings (`local.py`) as follows:

- Add `"greenlight",` to `INSTALLED_APPS`

Make sure that `fittings` and `eveuniverse` are also installed.

### Step 3: Finalizing the Installation<a name="step-4-finalizing-the-installation"></a>

Run static files collection and migrations

```shell
python manage.py collectstatic
python manage.py migrate
```

### Step 4: Setup Permissions<a name="step-4-setup-permissions"></a>

Now it's time to set up access permissions for your new greenlight module.

| ID                   | Description                       | Notes                                                                                                       |
| :------------------- | :-------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `basic_access` | Can access the greenlight module | Your line members should have this permission, together with everyone you want to have access to he module. |
| `can_manage_fleets`      | Can manage fleets                 | Everyone with this permission set status of the fleets                                                      |

