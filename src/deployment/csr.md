# การดีพลอยแอป CSR

หากคุณสร้างแอปที่ใช้เฉพาะการเรนเดอร์ฝั่งไคลเอนต์ โดยใช้ Trunk เป็นเซิร์ฟเวอร์สำหรับพัฒนาและเครื่องมือบิลด์ กระบวนการนี้ก็ค่อนข้างง่าย

```bash
trunk build --release
```

`trunk build` จะสร้างผลลัพธ์จากการบิลด์จำนวนหนึ่งไว้ในไดเรกทอรี `dist/` การนำ `dist` ไปเผยแพร่บนออนไลน์ก็เพียงพอสำหรับการดีพลอยแอปของคุณ วิธีนี้ควรทำงานคล้ายคลึงกับการดีพลอยแอปพลิเคชัน JavaScript ทั่วไปมาก

เราได้สร้างรีโพตัวอย่างหลายรีโพที่แสดงวิธีตั้งค่าและดีพลอยแอป Leptos CSR ไปยังบริการโฮสติ้งต่างๆ

_หมายเหตุ: Leptos ไม่ได้สนับสนุนให้ใช้บริการโฮสติ้งใดเป็นการเฉพาะ - คุณสามารถใช้บริการใดก็ได้ที่รองรับการดีพลอยเว็บไซต์แบบสแตติก_

ตัวอย่าง:

- [Github Pages](#github-pages)
- [Vercel](#vercel)
- [Spin (WebAssembly แบบเซิร์ฟเวอร์เลส)](#spin---webassembly-แบบเซิรฟเวอรเลส)
- [Netlify](#netlify)

## Github Pages

การดีพลอยแอป Leptos CSR ไปยัง Github Pages เป็นเรื่องง่ายดาย อย่างแรก ให้ไปที่การตั้งค่าของรีโพ Github ของคุณ แล้วคลิกที่ "Pages" ในเมนูด้านซ้าย ในส่วน "Build and deployment" ของหน้านั้น ให้เปลี่ยน "source" เป็น "Github Actions" จากนั้นคัดลอกสิ่งต่อไปนี้ไปยังไฟล์เช่น `.github/workflows/gh-pages-deploy.yml`

```admonish example collapsible=true

    name: Release to Github Pages

    on:
      push:
        branches: [main]
      workflow_dispatch:

    permissions:
      contents: write # for committing to gh-pages branch.
      pages: write
      id-token: write

    # Allow only one concurrent deployment, skipping runs queued between the run in-progress and latest queued.
    # However, do NOT cancel in-progress runs as we want to allow these production deployments to complete.
    concurrency:
      group: "pages"
      cancel-in-progress: false

    jobs:
      Github-Pages-Release:

        timeout-minutes: 10

        environment:
          name: github-pages
          url: ${{ steps.deployment.outputs.page_url }}

        runs-on: ubuntu-latest

        steps:
          - uses: actions/checkout@v4 # repo checkout

          # Install Rust Nightly Toolchain, with Clippy & Rustfmt
          - name: Install nightly Rust
            uses: dtolnay/rust-toolchain@nightly
            with:
              components: clippy, rustfmt

          - name: Add WASM target
            run: rustup target add wasm32-unknown-unknown

          - name: lint
            run: cargo clippy & cargo fmt


          # If using tailwind...
          # - name: Download and install tailwindcss binary
          #   run: npm install -D tailwindcss && npx tailwindcss -i <INPUT/PATH.css> -o <OUTPUT/PATH.css>  # run tailwind


          - name: Download and install Trunk binary
            run: wget -qO- https://github.com/trunk-rs/trunk/releases/download/v0.18.4/trunk-x86_64-unknown-linux-gnu.tar.gz | tar -xzf-

          - name: Build with Trunk
            # "${GITHUB_REPOSITORY#*/}" evaluates into the name of the repository
            # using --public-url something will allow trunk to modify all the href paths like from favicon.ico to repo_name/favicon.ico .
            # this is necessary for github pages where the site is deployed to username.github.io/repo_name and all files must be requested
            # relatively as favicon.ico. if we skip public-url option, the href paths will instead request username.github.io/favicon.ico which
            # will obviously return error 404 not found.
            run: ./trunk build --release --public-url "${GITHUB_REPOSITORY#*/}"

          # Copy index.html to 404.html for SPA routing
          # Will allow routing to work if client enters from any route
          # - name: Copy index.html to 404.html
          #   run: cp dist/index.html dist/404.html

          # Deploy to gh-pages branch
          # - name: Deploy 🚀
          #   uses: JamesIves/github-pages-deploy-action@v4
          #   with:
          #     folder: dist


          # Deploy with Github Static Pages

          - name: Setup Pages
            uses: actions/configure-pages@v5
            with:
              enablement: true
              # token:

          - name: Upload artifact
            uses: actions/upload-pages-artifact@v3
            with:
              # Upload dist dir
              path: './dist'

          - name: Deploy to GitHub Pages 🚀
            id: deployment
            uses: actions/deploy-pages@v4

```

สำหรับข้อมูลเพิ่มเติมเกี่ยวกับการดีพลอยไปยัง Github Pages [ดูรีโพตัวอย่างได้ที่นี่](https://github.com/diversable/deploy_leptos_csr_to_gh_pages)

## Vercel

### ขั้นตอนที่ 1: ตั้งค่า Vercel

ในส่วนติดต่อผู้ใช้เว็บของ Vercel...

1. สร้างโปรเจกต์ใหม่
2. ตรวจสอบให้แน่ใจว่า
   - "Build Command" ถูกเว้นว่างไว้โดยเปิด Override
   - "Output Directory" ถูกเปลี่ยนเป็น dist (ซึ่งเป็นไดเรกทอรีเอาต์พุตเริ่มต้นสำหรับบิลด์ของ Trunk) และเปิด Override

<img src="./image.png" />

### ขั้นตอนที่ 2: เพิ่มข้อมูลรับรองของ Vercel สำหรับ GitHub Actions

หมายเหตุ: ทั้งแอ็กชันพรีวิวและดีพลอยจะต้องมีการตั้งค่าข้อมูลรับรองของ Vercel ของคุณไว้ใน GitHub secrets

1. ดึง[Vercel Access Token](https://vercel.com/guides/how-do-i-use-a-vercel-api-access-token) ของคุณโดยไปที่ "Account Settings" > "Tokens" แล้วสร้างโทเคนใหม่ - บันทึกโทเคนไว้ใช้ในขั้นตอนย่อยที่ 5 ด้านล่าง

2. ติดตั้ง [Vercel CLI](https://vercel.com/cli) ด้วยคำสั่ง `npm i -g vercel` จากนั้นรัน `vercel login` เพื่อเข้าสู่ระบบบัญชีของคุณ

3. ภายในโฟลเดอร์ของคุณ ให้รัน `vercel link` เพื่อสร้างโปรเจกต์ Vercel ใหม่; ใน CLI คุณจะถูกถามว่า 'Link to an existing project?' - ให้ตอบ yes แล้วป้อนชื่อที่คุณสร้างในขั้นตอนที่ 1 โฟลเดอร์ `.vercel` ใหม่จะถูกสร้างให้คุณ

4. ภายในโฟลเดอร์ `.vercel` ที่สร้างขึ้น ให้เปิดไฟล์ `project.json` แล้วบันทึก "projectId" และ "orgId" ไว้สำหรับขั้นตอนถัดไป

5. ภายใน GitHub ให้ไปที่ "Settings" > "Secrets and Variables" > "Actions" ของรีโพ แล้วเพิ่มสิ่งต่อไปนี้เป็น [Repository secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets):
   - บันทึก Vercel Access Token ของคุณ (จากขั้นตอนย่อยที่ 1) เป็น secret ชื่อ `VERCEL_TOKEN`
   - จาก `.vercel/project.json` ให้เพิ่ม "projectID" เป็น `VERCEL_PROJECT_ID`
   - จาก `.vercel/project.json` ให้เพิ่ม "orgId" เป็น `VERCEL_ORG_ID`

<i>สำหรับคำแนะนำฉบับเต็ม ดู["ฉันจะใช้ Github Actions กับ Vercel ได้อย่างไร"](https://vercel.com/guides/how-can-i-use-github-actions-with-vercel)</i>

### ขั้นตอนที่ 3: เพิ่มสคริปต์ Github Action

สุดท้ายนี้ คุณก็พร้อมที่จะคัดลอกและวางสองไฟล์ - ไฟล์หนึ่งสำหรับการดีพลอย อีกไฟล์สำหรับพรีวิว PR - จากด้านล่างหรือจาก[โฟลเดอร์ `.github/workflows/` ของรีโพตัวอย่าง](https://github.com/diversable/vercel-leptos-CSR-deployment/tree/leptos_0.6/.github/workflows) ไปยังโฟลเดอร์ github workflows ของคุณเอง - จากนั้นเมื่อคุณคอมมิตหรือเปิด PR ครั้งถัดไป การดีพลอยจะเกิดขึ้นโดยอัตโนมัติ

<i>สคริปต์สำหรับดีพลอยโปรดักชัน: `vercel_deploy.yml`</i>

```admonish example collapsible=true

	name: Release to Vercel

	on:
	push:
		branches:
		- main
	env:
	CARGO_TERM_COLOR: always
	VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
	VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

	jobs:
	Vercel-Production-Deployment:
		runs-on: ubuntu-latest
		environment: production
		steps:
		- name: git-checkout
			uses: actions/checkout@v3

		- uses: dtolnay/rust-toolchain@nightly
			with:
			components: clippy, rustfmt
		- uses: Swatinem/rust-cache@v2
		- name: Setup Rust
			run: |
			rustup target add wasm32-unknown-unknown
			cargo clippy
			cargo fmt --check

		- name: Download and install Trunk binary
			run: wget -qO- https://github.com/trunk-rs/trunk/releases/download/v0.18.2/trunk-x86_64-unknown-linux-gnu.tar.gz | tar -xzf-


		- name: Build with Trunk
			run: ./trunk build --release

		- name: Install Vercel CLI
			run: npm install --global vercel@latest

		- name: Pull Vercel Environment Information
			run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

		- name: Deploy to Vercel & Display URL
			id: deployment
			working-directory: ./dist
			run: |
			vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }} >> $GITHUB_STEP_SUMMARY
			echo $GITHUB_STEP_SUMMARY

```

<i>สคริปต์สำหรับดีพลอยพรีวิว: `vercel_preview.yml`</i>

```admonish example collapsible=true

	# For more info re: vercel action see:
	# https://github.com/amondnet/vercel-action

	name: Leptos CSR Vercel Preview

	on:
	pull_request:
		branches: [ "main" ]

	workflow_dispatch:

	env:
	CARGO_TERM_COLOR: always
	VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
	VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

	jobs:
	fmt:
		name: Rustfmt
		runs-on: ubuntu-latest
		steps:
		- uses: actions/checkout@v4
		- uses: dtolnay/rust-toolchain@nightly
			with:
			components: rustfmt
		- name: Enforce formatting
			run: cargo fmt --check

	clippy:
		name: Clippy
		runs-on: ubuntu-latest
		steps:
		- uses: actions/checkout@v4
		- uses: dtolnay/rust-toolchain@nightly
			with:
			components: clippy
		- uses: Swatinem/rust-cache@v2
		- name: Linting
			run: cargo clippy -- -D warnings

	test:
		name: Test
		runs-on: ubuntu-latest
		needs: [fmt, clippy]
		steps:
		- uses: actions/checkout@v4
		- uses: dtolnay/rust-toolchain@nightly
		- uses: Swatinem/rust-cache@v2
		- name: Run tests
			run: cargo test

	build-and-preview-deploy:
		runs-on: ubuntu-latest
		name: Build and Preview

		needs: [test, clippy, fmt]

		permissions:
		pull-requests: write

		environment:
		name: preview
		url: ${{ steps.preview.outputs.preview-url }}

		steps:
		- name: git-checkout
			uses: actions/checkout@v4

		- uses: dtolnay/rust-toolchain@nightly
		- uses: Swatinem/rust-cache@v2
		- name: Build
			run: rustup target add wasm32-unknown-unknown

		- name: Download and install Trunk binary
			run: wget -qO- https://github.com/trunk-rs/trunk/releases/download/v0.18.2/trunk-x86_64-unknown-linux-gnu.tar.gz | tar -xzf-


		- name: Build with Trunk
			run: ./trunk build --release

		- name: Preview Deploy
			id: preview
			uses: amondnet/vercel-action@v25.1.1
			with:
			vercel-token: ${{ secrets.VERCEL_TOKEN }}
			github-token: ${{ secrets.GITHUB_TOKEN }}
			vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
			vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
			github-comment: true
			working-directory: ./dist

		- name: Display Deployed URL
			run: |
			echo "Deployed app URL: ${{ steps.preview.outputs.preview-url }}" >> $GITHUB_STEP_SUMMARY


```

ดู[รีโพตัวอย่างได้ที่นี่](https://github.com/diversable/vercel-leptos-CSR-deployment) สำหรับข้อมูลเพิ่มเติม

## Spin - WebAssembly แบบเซิร์ฟเวอร์เลส

อีกทางเลือกหนึ่งคือการใช้แพลตฟอร์มแบบเซิร์ฟเวอร์เลสอย่าง Spin แม้ว่า [Spin](https://github.com/fermyon/spin) จะเป็นโอเพนซอร์สและคุณสามารถรันมันบนโครงสร้างพื้นฐานของคุณเองได้ (เช่น ภายใน Kubernetes) แต่วิธีที่ง่ายที่สุดในการเริ่มต้นใช้ Spin ในโปรดักชันคือการใช้ Fermyon Cloud

เริ่มต้นด้วยการติดตั้ง [Spin CLI ตามคำแนะนำที่นี่](https://developer.fermyon.com/spin/v2/install) และสร้างรีโพ Github สำหรับโปรเจกต์ Leptos CSR ของคุณ หากคุณยังไม่ได้ทำ

1. เปิด "Fermyon Cloud" > "User Settings" หากคุณยังไม่ได้เข้าสู่ระบบ ให้เลือกปุ่ม Login With GitHub

2. ใน "Personal Access Tokens" ให้เลือก "Add a Token" ป้อนชื่อ "gh_actions" แล้วคลิก "Create Token"

3. Fermyon Cloud จะแสดงโทเคน; ให้คลิกปุ่มคัดลอกเพื่อคัดลอกไปยังคลิปบอร์ดของคุณ

4. ไปที่รีโพ Github ของคุณแล้วเปิด "Settings" > "Secrets and Variables" > "Actions" จากนั้นเพิ่มโทเคนของ Fermyon cloud ลงใน "Repository secrets" โดยใช้ชื่อตัวแปร "FERMYON_CLOUD_TOKEN"

5. คัดลอกและวางสคริปต์ Github Actions ต่อไปนี้ (ด้านล่าง) ลงในไฟล์ `.github/workflows/<SCRIPT_NAME>.yml` ของคุณ

6. เมื่อสคริปต์ 'preview' และ 'deploy' ทำงานอยู่ Github Actions จะสร้างพรีวิวเมื่อมีพูลรีเควสต์ และดีพลอยโดยอัตโนมัติเมื่อมีการอัปเดตไปยังแบรนช์ 'main' ของคุณ

<i>สคริปต์สำหรับดีพลอยโปรดักชัน: `spin_deploy.yml`</i>

```admonish example collapsible=true

	# For setup instructions needed for Fermyon Cloud, see:
	# https://developer.fermyon.com/cloud/github-actions

	# For reference, see:
	# https://developer.fermyon.com/cloud/changelog/gh-actions-spin-deploy

	# For the Fermyon gh actions themselves, see:
	# https://github.com/fermyon/actions

	name: Release to Spin Cloud

	on:
	push:
		branches: [main]
	workflow_dispatch:

	permissions:
	contents: read
	id-token: write

	# Allow only one concurrent deployment, skipping runs queued between the run in-progress and latest queued.
	# However, do NOT cancel in-progress runs as we want to allow these production deployments to complete.
	concurrency:
	group: "spin"
	cancel-in-progress: false

	jobs:
	Spin-Release:

		timeout-minutes: 10

		environment:
		name: production
		url: ${{ steps.deployment.outputs.app-url }}

		runs-on: ubuntu-latest

		steps:
		- uses: actions/checkout@v4 # repo checkout

		# Install Rust Nightly Toolchain, with Clippy & Rustfmt
		- name: Install nightly Rust
			uses: dtolnay/rust-toolchain@nightly
			with:
			components: clippy, rustfmt

		- name: Add WASM & WASI targets
			run: rustup target add wasm32-unknown-unknown && rustup target add wasm32-wasi

		- name: lint
			run: cargo clippy & cargo fmt


		# If using tailwind...
		# - name: Download and install tailwindcss binary
		#   run: npm install -D tailwindcss && npx tailwindcss -i <INPUT/PATH.css> -o <OUTPUT/PATH.css>  # run tailwind


		- name: Download and install Trunk binary
			run: wget -qO- https://github.com/trunk-rs/trunk/releases/download/v0.18.2/trunk-x86_64-unknown-linux-gnu.tar.gz | tar -xzf-


		- name: Build with Trunk
			run: ./trunk build --release


		# Install Spin CLI & Deploy

		- name: Setup Spin
			uses: fermyon/actions/spin/setup@v1
			# with:
			# plugins:


		- name: Build and deploy
			id: deployment
			uses: fermyon/actions/spin/deploy@v1
			with:
			fermyon_token: ${{ secrets.FERMYON_CLOUD_TOKEN }}
			# key_values: |-
				# abc=xyz
				# foo=bar
			# variables: |-
				# password=${{ secrets.SECURE_PASSWORD }}
				# apikey=${{ secrets.API_KEY }}

		# Create an explicit message to display the URL of the deployed app, as well as in the job graph
		- name: Deployed URL
			run: |
			echo "Deployed app URL: ${{ steps.deployment.outputs.app-url }}" >> $GITHUB_STEP_SUMMARY

```

<i>สคริปต์สำหรับดีพลอยพรีวิว: `spin_preview.yml`</i>

```admonish example collapsible=true

	# For setup instructions needed for Fermyon Cloud, see:
	# https://developer.fermyon.com/cloud/github-actions


	# For the Fermyon gh actions themselves, see:
	# https://github.com/fermyon/actions

	# Specifically:
	# https://github.com/fermyon/actions?tab=readme-ov-file#deploy-preview-of-spin-app-to-fermyon-cloud---fermyonactionsspinpreviewv1

	name: Preview on Spin Cloud

	on:
	pull_request:
		branches: ["main", "v*"]
		types: ['opened', 'synchronize', 'reopened', 'closed']
	workflow_dispatch:

	permissions:
	contents: read
	pull-requests: write

	# Allow only one concurrent deployment, skipping runs queued between the run in-progress and latest queued.
	# However, do NOT cancel in-progress runs as we want to allow these production deployments to complete.
	concurrency:
	group: "spin"
	cancel-in-progress: false

	jobs:
	Spin-Preview:

		timeout-minutes: 10

		environment:
		name: preview
		url: ${{ steps.preview.outputs.app-url }}

		runs-on: ubuntu-latest

		steps:
		- uses: actions/checkout@v4 # repo checkout

		# Install Rust Nightly Toolchain, with Clippy & Rustfmt
		- name: Install nightly Rust
			uses: dtolnay/rust-toolchain@nightly
			with:
			components: clippy, rustfmt

		- name: Add WASM & WASI targets
			run: rustup target add wasm32-unknown-unknown && rustup target add wasm32-wasi

		- name: lint
			run: cargo clippy & cargo fmt


		# If using tailwind...
		# - name: Download and install tailwindcss binary
		#   run: npm install -D tailwindcss && npx tailwindcss -i <INPUT/PATH.css> -o <OUTPUT/PATH.css>  # run tailwind


		- name: Download and install Trunk binary
			run: wget -qO- https://github.com/trunk-rs/trunk/releases/download/v0.18.2/trunk-x86_64-unknown-linux-gnu.tar.gz | tar -xzf-


		- name: Build with Trunk
			run: ./trunk build --release


		# Install Spin CLI & Deploy

		- name: Setup Spin
			uses: fermyon/actions/spin/setup@v1
			# with:
			# plugins:


		- name: Build and preview
			id: preview
			uses: fermyon/actions/spin/preview@v1
			with:
			fermyon_token: ${{ secrets.FERMYON_CLOUD_TOKEN }}
			github_token: ${{ secrets.GITHUB_TOKEN }}
			undeploy: ${{ github.event.pull_request && github.event.action == 'closed' }}
			# key_values: |-
				# abc=xyz
				# foo=bar
			# variables: |-
				# password=${{ secrets.SECURE_PASSWORD }}
				# apikey=${{ secrets.API_KEY }}


		- name: Display Deployed URL
			run: |
			echo "Deployed app URL: ${{ steps.preview.outputs.app-url }}" >> $GITHUB_STEP_SUMMARY

```

ดู[รีโพตัวอย่างได้ที่นี่](https://github.com/diversable/leptos-spin-CSR)

# Netlify

การดีพลอยแอป Leptos CSR ไปยัง Netlify ต้องทำเพียงสร้างโปรเจกต์และเพิ่มไฟล์การกำหนดค่าอย่างง่ายสองไฟล์ไว้ในรูทของโปรเจกต์ของคุณ มาเริ่มจากอย่างหลังกันเลย

## ไฟล์การกำหนดค่า

สร้างไฟล์ `netlify.toml` ในรูทของโปรเจกต์ของคุณโดยมีเนื้อหาดังนี้:

```toml
[build]
command = "rustup target add wasm32-unknown-unknown && cargo install trunk --locked && trunk build --release"
publish = "dist"

[build.environment]
RUST_VERSION = "stable"

[[redirects]]
from = "/*"
to = "/index.html"
status = 200
```

สร้างไฟล์ `rust-toolchain.toml` ในรูทของโปรเจกต์ของคุณโดยมีเนื้อหาดังนี้:

```toml
[toolchain]
channel = "stable"
targets = ["wasm32-unknown-unknown"]
```

## การดีพลอย

1. [เพิ่มโปรเจกต์ของคุณไปยัง Netlify](https://docs.netlify.com/start/add-new-project/) โดยเชื่อมต่อรีโพ Git ของคุณ
2. Netlify จะตรวจจับการกำหนดค่า `netlify.toml` ของคุณโดยอัตโนมัติ
3. หากคุณต้องการตัวแปรสภาพแวดล้อมเพิ่มเติม ให้กำหนดค่าเหล่านั้นใน[การตั้งค่าตัวแปรสภาพแวดล้อมของ Netlify](https://docs.netlify.com/build/environment-variables/overview/)

ไฟล์ `rust-toolchain.toml` ช่วยให้มั่นใจว่ามี toolchain ของ Rust และเป้าหมาย WASM ที่ถูกต้องพร้อมใช้งานระหว่างกระบวนการบิลด์ ส่วนกฎการเปลี่ยนเส้นทาง (redirect) ใน `netlify.toml` ช่วยให้เส้นทาง SPA ของคุณทำงานได้อย่างถูกต้องโดยการเสิร์ฟ `index.html` สำหรับทุกพาธ
