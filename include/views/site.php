<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<link href="/css/mailcheck.css?=<?=$this->SCRIPT_VERSION?>" rel="stylesheet" type="text/css" />
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>MailCheck</title>
	
	<script type="text/javascript" src="/js/jquery-1.3.1.min.js"></script>
	<script type="text/javascript" src="/js/mailcheck.js?=<?=$this->SCRIPT_VERSION?>"></script>
	<script type="text/javascript">
		var Translations = {
			ok:{
				header: '<?=$this->_('All tests are OK:')?>',
				header_all: '<?=$this->_('All finished tests are OK:')?>'
			},
			warning: { header: '<?=$this->_('Warnings found in test:')?>'},
			error: { header: '<?=$this->_('Errors found in the test:')?>' },
			denied: { header: '<?=$this->_('Too many tests has been run against:')?>', header2: '<?=$this->_('Test denied:')?>'},
			running: { header: '<?=$this->_('Running test...')?>' },
			loading: {
				header: '<?=$this->_('Loading')?>',
				label: '<?=$this->_('Waiting for the test results to be loaded')?>'
			},
			queued: {
				header: '<?=$this->_('Test queued...')?>',
				label: '<?=$this->_('Waiting for the test to start')?>'
			},
			notFound: {
				header: "<?=$this->_('Not found')?>",
				label: "<?=$this->_('The test you are looking for doesn\'t exist')?>"
			}
		};

		var g_test = new Test();
		g_test.init();
		var g_history = new History();
		var g_response = false;
		var extra = '';

		$(document).ready(function(){
			g_history.init();
		});

		<?php if ($this->allowRelay): ?>
			extra = 'OpenRelay';
		<?php endif; ?>
	</script>
</head>

<body>

<div id="wrapper">
	<div id="top">
		<h1 id="logo_mailcheck">
			<a href="/"><span>MailCheck</span></a>
		</h1>
		<h2 id="logo_se">
			<a href="http://www.iis.se/en">
				<span><?php echo(translate("A service from .SE"));?></span>
			</a>
		</h2>
		<div class="clear"> </div>
		<div id="searchbox">
			<h3 id="searchhead"><?php echo(translate("Test your Mail-server and find errors"));?></h3>

			<form id="mainform" action="/test.php" method="post">
				<div id="standard-input">
				<div id="testinput">
					<div class="testinput-title"><?=translate('E-mail address:')?></div>
					<div class="domaininput-box">
						<input type="text" id="domaininput"/>
					</div>
				</div>
				<p id="testtext"><?php echo(translate("Enter your e-mail address in the field above to test your server."));?></p>
			
				<div id="slow-tests-checkbox" style="font-size: 0.8em">
				<input type="checkbox" id="slow-tests" /><label for="slow-tests"><?=translate('Run outgoing mail tests')?></label>
				</div>
				
				<p id="testbutton">
					<a href="#" onclick="return startTest($('#domaininput').val(), extra);" id="testnow" class="button-enabled button"><?php echo(translate("Test now"));?></a>
				</p>
				</div>
				<div id="dialogs">
					<div id="dialog_1" class="dialog" style="display: none">
						<div class="dialog-top"></div>
						<div class="dialog-content">
							<p>
								<?=translate('Do you use a local email client like Outlook or Thunderbird? Or, do you use a web based email client?')?>
							</p>
							<p>
								<a href="#" onclick="$('.dialog').hide(); $('#dialog_2').slideDown(); return false;"><?=translate('Local email client')?></a>
								<?=translate('or')?> 
								 <a href="#" onclick="$('.dialog').hide(); $('#dialog_3').slideDown(); return false;"><?=translate('Web based client')?></a>
							</p>
						</div>
						<div class="dialog-bottom"></div>
					</div>
					<div id="dialog_2" class="dialog" style="display: none;">
						<div class="dialog-top"></div>
						<div class="dialog-content">
							<p><?=translate('To start the test you must send an email using your local email client. When the email is sent, click on the "Start Test" button.')?></p>
							<p><?=translate('Click on the link below to send the email:')?></p>
							 <a id="d2-mailto-ol-link" href=""><?=translate('Send email using Outlook')?></a><br/>
							 <a id="d2-mailto-link" href=""><?=translate('Send email using other clients')?></a>

							<div class="dialog-button-holder">
								<div class="dialog-button-back">
									<img src="/images/bg_linkback.png" style="margin-right: 3px" /><a href="#" onclick="$('#dialog_2').hide(); $('#dialog_1').slideDown(); return false;">Back</a>
								</div>
								<p style="padding: 0px; margin: 10px 0 0 0;font-size:1.25em">
									<a href="#" style="margin-bottom: 0;" onclick="emailsSent(); return false;" id="testnow" class="button-enabled button"><?=translate("Start test");?></a>
								</p>
							</div>
						</div>
						<div class="dialog-bottom"></div>
					</div>
					<div id="dialog_3" class="dialog" style="display: none">
						<div class="dialog-top"></div>
						<div class="dialog-content">
						<p><?=translate('Start your email client and send an email with the following settings:')?></p>
							<ul>
								<li><?=translate('To:')?> <span id="d3-email"></span></li>
								<li><?=translate('Subject:')?> <span id="d3-subject"></span></li>
								<li><?=translate('Body:')?> <span id="d3-body"></span></li>
							</ul>

							<div class="dialog-button-holder">
								<div class="dialog-button-back">
								<img src="/images/bg_linkback.png" style="margin-right: 3px" /><a href="#" onclick="$('#dialog_3').hide(); $('#dialog_1').slideDown(); return false;"><?=translate('Back')?></a>
								</div>
								<p style="padding: 0px; margin: 10px 0 0 0; font-size:1.25em">
									<a href="#" style="margin-bottom: 0;" onclick="emailsSent(); return false;" id="testnow" class="button-enabled button"><?=translate("Start test");?></a>
								</p>
							</div>
						</div>
						<div class="dialog-bottom"></div>
						
					</div>
					<div class="jquery-ie-fix"></div>
				</div>
			</form>
		</div>

		<div id="menu">
			<ul>
				<li><a href="/"><?php echo(translate("Home")); ?></a></li>
				<li><a href="/?donttestme"><?php echo(translate("I don't want to be tested")); ?></a></li>
				<li><a href="/wiki"><?php echo(translate("Technical info")); ?></a></li>
				<li><a href="/?bugreport"><?=$this->_('Bug report')?></a></li>
				<li><a href="/?cookies"><?=$this->_('About cookies')?></a></li>
				<li><a href="/?website"><?=$this->_('The website')?></a></li>
			</ul>
		</div>
		<div class="clear"> </div>
	</div>

	<div style="padding-top: 1px">
		<div></div>

		<div id="error_box" style="display:none">
			<div style="width: 420px;">
				<div id="error_box_light" class="mainerror">&nbsp;</div>
				<h3 style="margin-top: 20px; width: 345px"><?=$this->_('Please enter a valid email address')?></h3>
			</div>
			<div id="error_box_bottom"> </div>
		</div>
		
		<div id="result_running" style="display: none">
			<div style="float: left; width: 420px;">
				<div id="running_light" class="mainload">&nbsp;</div>
				<h3 id="running_header" style="width: 345px"><?=translate('Running...')?></h3>
				<p id="running_text" style="width: 345px">live feedback goes here</p>
				<div id="running_customMessage" class="status_customMessage" style="width:345px"></div>
			</div>
			<div id="status_bottom"> </div>
		</div>

		<div id="result_status" style="display:none">
			<div style="float: left; width: 420px;">
				<div id="status_light" class="mainload">&nbsp;</div>
				<h3 id="status_header" style="width: 345px"></h3>
				<p id="status_text" style="width: 345px"></p>
				<div id="status_customMessage" class="status_customMessage" style="width:345px"></div>
			</div>
			<div id="status_bottom"> </div>
		</div>
		<div>
			<div id="result-status-gold" class="result-status result-status-gold information-box" style="display: none">
				<div class="result-dialog-width">
					<div id="status-gold-light" class="mainload">&nbsp;</div>
					<h3 id="status-gold-header"></h3>
					<p id="status-gold-text"></p>
					<div id="status-gold-customMessage" class="status_customMessage" style="display: none"></div>
				</div>
				<div  class="result-status-gold-bottom"> </div>
			</div>

			<div style="display:none" id="gold_box" class="gold-box information-box">
				<div class="result-dialog-width">
					<div style="float: left;" id="status_gold">
						<div class="gold-box-image">
						</div>
					</div>

					<div style="float: left; width: 300px">
						<h3 style="margin: 10px 0 0 10px"><span id="status_gold_count"></span><?=translate('gold stars awarded')?></h3>
						<p style="margin-left: 10px"><?=translate('for excellence in mail server setup')?></p>
					</div>
				</div>
				<div class="gold-box-bottom" > </div>
			</div>
		</div>
	</div>
	
	<div style="clear: both">
		<?=$this->PAGE_CONTENT?>	
	</div>	
	<div id="footer">
		<p id="f_info">
			<a href="http://www.iis.se/en"><?php echo(translate(".SE (The Internet Infrastructure Foundation)"));?></a>
		</p>

<?php /* disabled until proper translations are in place
		<p id="f_links">
			<?=Config::get('MAILCHECK_VERSION')?>	
		</p>
		<p id="f_lang">
			<?php echo(translate('Language'));?>:
			<select id="language">
<?php if ($this->language == 'en_US'): ?>
				<option value="en_US" selected="selected">English</a>
				<option value="sv_SE">Svenska</a>
<?php else: ?>
				<option value="sv_SE" selected="selected">Svenska</a>
				<option value="en_US">English</a>
<?php endif; ?>
			</select>
		</p>
 */ ?>

		<p id="f_lang">
			<?=Config::get('MAILCHECK_VERSION')?>	
		</p>

		<br class="clear" />
	</div>
	
	<script type="text/javascript">
		<!--
		$('#domaininput').keydown(function(e){
			if (e.keyCode == 13)
			{
				startTest($('#domaininput').val());
				return false;
			}
		});
		-->
	</script>
</div>
</body>
</html>
