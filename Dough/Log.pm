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

sub __output {
    my ($s, $level, $str) = @_;

    my $fh = $s->{handle};
    my ($pkg, $fname, $line) = caller(1);
    print STDERR "$s $level $fname:$line $str\n", if ($level);

	print $fh scalar(localtime()) . " - $level - " . sprintf("%-30s", "$fname:$line") . 
        " \"$str\"\n", if (defined($fh) && defined($str));

    for ($i = 0; $i < $level; $i++) {
        my ($pkg, $fn, $ln, $sub, $hash, $warray, $eval, $isr) = caller($i+1);
        print $fh ' 'x($i+28) . " +- $pkg - $fn - $ln - $sub - $hash - $warray - $eval - $isr\n";
    }
}

sub log {
    $_[0]->__output(0, $_[1]); 
}

sub debug {
    $_[0]->__output(1, $_[1]);
}

sub sep {
    my $fh = $_[0]->{handle};
    print $fh "" . ' 'x25 . '-'x50 . "\n";
}

sub sepWStr {
    my ($s, $str) = @_;
    $str = ">> $str";
    my $fh = $s->{handle};
    my $ls = length($str);

    print $fh "$str" . (($ls < 25) ? ' 'x(25-$ls) : '') . '-'x50 . "\n";
}

1;
