# ASTrace: A Structural Approach to Code Provenance and Mitigating Generative Model Collapse

**Author:** Arna Nandi  
**Published Prior Art DOI:** 10.5281/zenodo.20679888 
**Date:** June 2026  
**License:** Open Access / MIT (Defensive Publication)  

## Abstract
As large language models increasingly ingest programmatic data from public repositories, the phenomenon of "Model Collapse"—driven by the recursive training on synthetic, unverified code—presents a significant challenge to dataset integrity. While traditional lexical watermarks offer foundational attribution, they are inherently susceptible to standardization by automated syntax formatters. This paper proposes ASTrace, an architecture that embeds a cryptographic signature directly into the Abstract Syntax Tree (AST) of the source code. By deterministically transposing commutative mathematical nodes, isolating leaf-node execution, and injecting domain-contextualized asymmetrical padding, ASTrace establishes a robust, transformation-invariant provenance mechanism. This approach ensures runtime stability and preserves the cryptographic signature across diverse software engineering environments.

## I. Introduction
The curation of pristine, human-generated training data is critical for the continued advancement of generative artificial intelligence. The inadvertent integration of synthetic, AI-generated code into training pipelines can lead to mathematical distribution shifts, commonly referred to as Model Collapse. Establishing reliable data provenance is therefore a priority for the research community.

Current methodologies often utilize lexical watermarking—such as specific comment structures or variable naming conventions. While conceptually sound, these methods experience practical limitations in modern software environments where automated formatting tools (e.g., Black, Prettier) are standard practice. Because formatters normalize lexical representations, surface-level watermarks are frequently discarded during routine code maintenance. This necessitates a paradigm shift towards structural attribution methodologies that persist independent of typographical layout.

## II. Structural Transposition of the Abstract Syntax Tree
To achieve format-agnostic provenance, ASTrace operates at the compiler level by manipulating the Abstract Syntax Tree (AST). The core mechanism leverages the mathematical property of commutativity within binary operations, specifically addition and multiplication.

Because the expressions `A + B` and `B + A` yield identical execution states, their logical nodes can be safely transposed. ASTrace utilizes a SHA-256 cryptographic hash of a user-defined key to generate a 256-bit sequence. During AST traversal, the engine aligns the absolute alphabetical weight of the left and right operational branches with the corresponding bit in the cryptographic sequence. This embeds a persistent mathematical fingerprint into the program's structural graph, rendering it entirely immune to lexical standardizations.

## III. Execution Safety and Cryptographic Synchronization
Manipulating an Abstract Syntax Tree introduces inherent risks to runtime logic and verification fidelity. To ensure absolute programmatic stability, ASTrace enforces two strict architectural constraints.

### A. Mitigation of Short-Circuit Evaluation Risks
Unlike basic arithmetic, Boolean logic (such as logical AND/OR) evaluates sequentially. Altering the order of conditional statements may result in fatal runtime errors if dependencies are not met (short-circuiting). Consequently, the ASTrace engine employs a pre-processing safety scanner that exclusively isolates pure mathematical nodes (`ast.Add`, `ast.Mult`) and entirely bypasses any branches containing function calls or complex conditionals.

### B. Leaf-Node Isolation and Graph Inversion Prevention
A significant challenge in structural cryptography is maintaining synchronization between the encoder and the decoder. If a parent mathematical node is transposed, the sequential reading order of its nested child nodes is inverted, which can desynchronize the signature extraction process. To resolve this, ASTrace utilizes "Leaf-Node Isolation." The engine is constrained to transpose only terminal mathematical nodes that do not contain further nested operations. This guarantees that the verification decoder evaluates the tree in the precise chronological order intended by the encoder, yielding a 100% verification confidence interval.

## IV. Asymmetrical Entropy Injection and Domain Camouflage
A robust cryptographic signature requires sufficient physical nodes (entropy) to store the bitstream. Concise programmatic scripts may lack the natural nodes required for a secure SHA-256 hash. ASTrace addresses this through the autonomous injection of opaque predicates—artificial mathematical operations that evaluate benignly (e.g., `1 + 2`).

Crucially, this padding is *asymmetrical*. Utilizing distinct integers ensures that when the engine transposes the node to `2 + 1`, the alteration is distinctly readable by the decoder. To ensure these injected variables are not flagged or removed during routine human code review, ASTrace employs Contextual Stealth Padding, aligning the injection syntax with the specific domain of the host application:

* **Web Server Frameworks:** Nodes are integrated into dictionary structures mimicking backend telemetry mapping (e.g., `_INTERNAL_TELEMETRY_MAP`).
* **Machine Learning Pipelines:** Padding is formatted as static tensor initializations or matrix weight buffers.
* **Cybersecurity Networking:** Operations are structured as predefined packet buffer allocations or socket configurations.
* **Game Engine Development:** Entropy is disguised as boundary coordinate caches for sprite rendering.
* **Systems / DevOps Automation:** Variables are formatted as standard operating system exit codes or memory offsets.
* **Data Science Libraries:** Padding takes the form of standalone, global memory flag allocations.

## V. Conclusion
The preservation of human-authored datasets is imperative for the trajectory of machine learning. By migrating provenance signatures from the fragile lexical layer to the resilient structural layer of the Abstract Syntax Tree, ASTrace provides a mathematically verifiable, execution-safe mechanism for code attribution. Through the integration of leaf-node isolation and context-aware entropy padding, this architecture offers a highly scalable and unobtrusive framework suitable for diverse enterprise and open-source ecosystems.
