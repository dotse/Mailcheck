<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<link href="/css/mailcheck.css" rel="stylesheet" type="text/css" />
	<link href="/css/admin.css" rel="stylesheet" type="text/css" />
	
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>MailCheck Administration</title>
	
	<script type="text/javascript" src="/js/jquery-1.3.1.min.js"></script>
	<script type="text/javascript" src="/js/admin.js"></script>
</head>

<body>
	<div id="wrapper">

		<div>
			<h2>Administration</h2>
		</div>
		
		<div style="padding: 0 0 20px 0">
			<?=$this->PAGE_CONTENT?>
		</div>

		<div id="footer">
			<p id="f_info"><?php echo(translate(".SE (The Internet Infrastructure Foundation)"));?></p>
			<br class="clear" />
		</div>
	</div>
</body>
</html>
