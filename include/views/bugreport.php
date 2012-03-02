<div>
	<div class="lower-dialog">
		<h3><?=$this->_('Bug report')?></h3>
		<div class="lower-dialog-box">
			<?php if ($this->saved == true): ?>
			<div>
			<div style=" padding-bottom: 15px"><?=translate('Thank you,')?></div>
				<?=$this->_('Your bug report has been received')?>
			</div>
			<?php else: ?>
			<form action="/?bugreport" method="post" onsubmit="return checkSubmit();">
				<input type="hidden" name="action" value="bugreport" />
				<div><?=$this->_('Description')?>:</div>
				<div><textarea name="description" style="width: 100%; height: 120px" ><?=$this->desc?></textarea></div>
				<div class="bug-report-row">
					<div><?=$this->_('Email (Optional)')?>:</div>
					<input id="bug-report-email" type="text" name="email" style="width: 250px" value="<?=$this->email?>"/>
					<span id="email-error-message" style="color: red; display:none"><?=$this->_('Invalid email')?></span>
				</div>
				
				<div class="bug-report-row">
					<div><?=$this->_('Fill in the code below')?>:</div>
					<img id="captcha" src="/securimage/securimage_show.php" alt="<?=$this->_('Code')?>" />
					<a href="#" onclick="document.getElementById('captcha').src = '/securimage/securimage_show.php?' + Math.random(); return false">
						<img src="/images/arrow_refresh.png" alt="<?=$this->_('Refresh code')?>">
					</a>
					<div>
						<input type="text" name="captcha_code" size="10" maxlength="6" />
						<?php if ($this->wrongCode): ?>
						<span style="color: red"><?=$this->_('Wrong code')?></span>
						<?php endif; ?>
					</div>
				</div>
				<div class="bug-report-row">
					<input type="submit" value="<?=$this->_('Submit report')?>"/>
				</div>
			</form>
			<script type="text/javascript">
			<!--
				function checkSubmit()
				{
					var email = $('#bug-report-email');
					if (email.val() != '' && validateEmail(email.val()) == false)
					{
						$('#email-error-message').show();
						return false;
					}
					return true;
				}
			-->
			</script>
			<?php endif; ?>
		</div>
	</div>
</div>
