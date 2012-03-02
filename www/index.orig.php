<?php

require_once dirname(__FILE__) . '/../include/common.php';

$template = new Template('site');

//
// Save bug report
//
if (isset($_POST['action']) && $_POST['action'] == 'bugreport')
{
	session_start(); 
	$request = Request::getCurrentRequest();

	include_once dirname(__FILE__) . '/securimage/securimage.php';
	$securimage = new Securimage();
	
	$params = array(
		$request->POST('description', 'string'),
		$request->POST('email', 'email'),
	);

	if ($securimage->check($_POST['captcha_code']))
	{
		Database::query('INSERT INTO bug_report (description, email) values(?,?)', $params);
                $bugreport_email= Config::get('bugreportEmail');
		mail($bugreport_email, "Bug report", "Reported by: ".$params[1]."\nDescription:\n".$params[0]."\n");
	
		$template->saved = true;
	}
	else
	{
		$template->wrongCode = true;
		$template->desc = $params[0];
		$template->email = $params[1];
	}

	$template->render('bugreport');
}
//
// Create bug reports
//
else if (isset($_GET['bugreport']))
{
	$template->render('bugreport');
}
//
// The website
//
else if (isset($_GET['website']))
{
	$template->render('website');
}
//
// About Cookies
//
else if (isset($_GET['cookies']))
{
	$template->render('cookies');
}
//
// Dont test me
//
else if (isset($_GET['donttestme']) && isset($_GET['key']))
{
	$inputKey = $template->_request()->GET('key', 'hash');
	$email = $template->_request()->GET('email', 'email');
	$template->blacklisted = false;

	$e = explode('@', $email, 2);
	if (count($e) == 2)
	{
		$key = md5("mchammer" . $e[0] . 'jdDFJ45gb!#aFS_@f93u7' . $e[1]);

		if ($inputKey == $key)
		{
			$params = array($e[1], 0, 0, $email, $_SERVER['REMOTE_ADDR'], $email);
			$domains = Database::query('SELECT domain FROM frequency WHERE domain = ? LIMIT 1', array($e[1]));
			if (is_array($domain) == false)
				Database::query('INSERT INTO frequency (domain, max_tests, interval, created_email, created_ip, description) VALUES(?,?,?,?,?,?)', $params);
			$template->blacklisted = true;
		}
	}

	$template->render('donttestme');
}
else if (isset($_GET['donttestme']) && !empty($_POST))
{
	$request = Request::getCurrentRequest();
	$email = $request->POST('email', 'email'); 
	$email2 = $request->POST('email2', 'email'); 

	if (Validation::validate($email, 'email') == false)
		$template->error = $template->_('Please enter a valid email address');
	else if ($email != $email2)
		$template->error = $template->_('Email addresses do not match');
	else
	{ // All good
		$e = explode('@', $email, 2);
		$key = md5("mchammer" . $e[0] . 'jdDFJ45gb!#aFS_@f93u7' . $e[1]);
		mail($email, "MailCheck - Blacklist", "Click the following link to blacklist your domain: http://".$_SERVER['SERVER_NAME']."/?donttestme&email=".$email."&key=".$key."\n");

		$template->done = true;
	}

	$template->render('donttestme');
}
else if (isset($_GET['donttestme']))
{
	$template->render('donttestme');
}

//
// Index
//
else
{
	$relay = isset($_GET['relaytestallowed']) ? true : false;
	$template->allowRelay = $relay;

	$template->render('index');
}
