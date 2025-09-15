nextflow.enable.dsl=2

process TRIM_READS {
    container 'bio-comp/ngs-containers/cutadapt:latest'

    input:
    path fastq

    output:
    path "trimmed.fastq.gz"

    script:
    """
    cutadapt -a AGATCGGAAG -o trimmed.fastq.gz ${fastq}
    """

    workflow {
        // channel from input param
        ch_input_reads = Channel.fromPath(params.input)

        // call
        TRIM_READS(ch_input_reads)
    }
}