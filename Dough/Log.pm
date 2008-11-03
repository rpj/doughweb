package Dough::Log;

use Dough::Config;

my $singleton;

sub new {
	unless (defined($singleton)) {
		my $class = shift;
		my $self = { file => $k_logFile };

		open ($self->{handle}, "+>>$self->{file}")
			or print STDERR "Dough::Log unable to open log file '$self->{file}': $!\n\n";

		$singleton = bless($self, $class);
	}

	return $singleton;
}

sub instance {
	return ($singleton || (shift)->new());
}

sub log {
	my ($s, $str) = @_;
	my $fh = $s->{handle};
	print $fh "$str\n", if (defined($fh) && defined($str));
}

1;
