<div id="startwrapper">
	<h3><?=$this->_("Don't test me")?></h3>
	<div class="startbox">
		<?php if ($this->blacklisted !== ''): ?>
			<?php if ($this->blacklisted == true): ?>
				<?=$this->_('Your domain will no longer be tested')?>.
			<?php else: ?>
				<?=$this->_('Invalid key used when trying to blacklist the domain')?>.
			<?php endif; ?>	
		<?php elseif (!$this->done): ?>
		<form id='donttestme' method='post' action='/?donttestme'>
			<div class="dont-test">
				<div class="clear">
					<span class="dont-test-label"><?=$this->_('E-mail address')?>:</span>
					<input type='text' name='email' class='dont-test-input' value="" />
				</div>
				<div class="clear">
					<label class="dont-test-label"><?=$this->_('Confirm email')?>:</label>
					<input type='text' name='email2' class='dont-test-input' />
				</div>
			</div>
			<?php if ($this->error): ?>
				<div class="dont-test-error clear"><?=$this->error?></div>
			<?php endif; ?>

			<p class="clear">
				<?=$this->_("To disable further testing against your domain enter you're email address and click on the link in the email you'll recieve")?>
			</p>
			<p class="donttestbutton"><a href="#" onclick="$('#donttestme').submit()" class='button' id="donttestbutton">
				<?=$this->_("Don't test me!")?></a>
			</p>
		</form>
		<?php else: ?>
			<?=$this->_('Please check your email and click on the link in the email to stop your domain from being tested')?>.
		<?php endif; ?>
	</div>
</div>
