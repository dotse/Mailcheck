<div id="startwrapper">
	<?php if (isset($_GET['faq'])): ?>
		<h3><?php echo(translate("MailCheck FAQ")); ?></h3>
		<div class="startbox">
		<?php echo(translate("MailCheck FAQ contents"));?>
		</div>
	<?php elseif (isset($_GET['blacklist'])): ?>
		<h3><?php echo(translate("No tests will be run against your domain"));?></h3>
		<?php echo(translate("No tests will be run against your domain, please contact us to allow tests against your domain again"));?>
	<?php else: ?>
		<h3><?php echo(translate("About MailCheck"));?></h3>
		<div class="startbox">
		<p style="margin-top:0"><?=translate('Mailcheck is a free, automated online test tool which lets users test many different quality-related aspects of their email setup.')?></p>
		<p><?=translate('Mailcheck aims to improve the overall quality of email related services on the Internet by pointing out possible configuration problems, software flaws or standards violations to system administrators and end users.')?></p>
		</div>
	<?php endif; ?>
</div>
