nextflow.enable.dsl = 2

// ---- params ----
params.input = "${baseDir}/data/*.fastq.gz"
// SE glob
params.paired = false
// set true for PE
params.pat = ~/(_R)?([12])\.f(ast)?q\.gz$/
// PE pairing regex
params.adapter_r1 = 'AGATCGGAAGAGC'
// 3' adapter R1
params.adapter_r2 = 'AGATCGGAAGAGC'
// 3' adapter R2 (usually same Illumina 3' motif)

// ---- Single-end ----
process TRIM_SE {
    tag "${sample_id}"
    container 'quay.io/biocontainers/cutadapt:4.6--py311h331c9d8_0'
    cpus 2
    memory '2 GB'
    time '1h'

    input:
    tuple val(sample_id), path(r1)

    output:
    tuple val(sample_id), path("${sample_id}.trimmed.fastq.gz")

    script:
    """
  cutadapt \
    -a ${params.adapter_r1} \
    -q 20 -m 20 \
    -o ${sample_id}.trimmed.fastq.gz \
    ${r1}
  """
}

// ---- Paired-end ----
process TRIM_PE {
    tag "${sample_id}"
    container 'quay.io/biocontainers/cutadapt:4.6--py311h331c9d8_0'
    cpus 4
    memory '4 GB'
    time '2h'

    input:
    tuple val(sample_id), path(r1), path(r2)

    output:
    tuple val(sample_id), path("${sample_id}_R1.trimmed.fastq.gz"), path("${sample_id}_R2.trimmed.fastq.gz")

    script:
    """
  cutadapt \
    -a ${params.adapter_r1} \
    -A ${params.adapter_r2} \
    -q 20,20 -m 20 \
    -o ${sample_id}_R1.trimmed.fastq.gz \
    -p ${sample_id}_R2.trimmed.fastq.gz \
    ${r1} ${r2}
  """
}

workflow {
    if (params.paired) {
        // Build (id, R1, R2) tuples from paired files
        Channel.fromFilePairs(params.input, flat: false, size: 2, fileExtensions: ['.fq.gz', '.fastq.gz'], mode: 'paired')
            .map { id, pair -> tuple(id, pair[0], pair[1]) }
            .set { ch_pe }

        trimmed_pe = TRIM_PE(ch_pe)
        trimmed_pe.view { id, r1, r2 -> "TRIMMED-PE: ${id} -> ${r1.name}, ${r2.name}" }
    }
    else {
        Channel.fromPath(params.input, checkIfExists: true)
            .map { f -> tuple(f.baseName, f) }
            .set { ch_se }

        trimmed_se = TRIM_SE(ch_se)
        trimmed_se.view { id, f -> "TRIMMED-SE: ${id} -> ${f.name}" }
    }
}
