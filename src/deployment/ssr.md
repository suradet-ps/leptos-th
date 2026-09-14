# การดีพลอยแอป SSR แบบฟูลสแตก

คุณสามารถดีพลอยแอป Leptos แบบฟูลสแตกที่ใช้ SSR ไปยังบริการโฮสติ้งหรือคอนเทนเนอร์ใด ๆ ก็ได้ตามต้องการ วิธีที่ง่ายที่สุดในการนำแอป Leptos SSR ขึ้นโปรดักชันอาจเป็นการใช้บริการ VPS แล้วรันไบนารี Leptos แบบเนทีฟใน VM ([ดูรายละเอียดเพิ่มเติมได้ที่นี่](https://github.com/leptos-rs/start-axum?tab=readme-ov-file#executing-a-server-on-a-remote-machine-without-the-toolchain)) หรืออีกทางเลือกหนึ่ง คุณสามารถทำคอนเทนเนอร์ (containerize) แอป Leptos แล้วรันด้วย [Podman](https://podman.io/) หรือ [Docker](https://www.docker.com/) บนเซิร์ฟเวอร์แบบโคโลเคชัน (colocated) หรือคลาวด์ใดก็ได้

รูปแบบการดีพลอยและบริการโฮสติ้งมีให้เลือกหลากหลายมาก และโดยทั่วไปตัว Leptos เองไม่ได้ผูกมัดกับวิธีใดวิธีหนึ่งเป็นการเฉพาะ ด้วยความยืดหยุ่นของเป้าหมายการดีพลอยที่มีมากมาย ในหน้านี้เราจะกล่าวถึง:

- [การสร้าง `Containerfile` (หรือ `Dockerfile`) สำหรับใช้กับแอป Leptos SSR](#การสราง-containerfile)
- การใช้ `Dockerfile` เพื่อ[ดีพลอยไปยังบริการคลาวด์](#การดีพลอยบนคลาวด) - [ตัวอย่างเช่น Fly.io](#การดีพลอยไปยัง-flyio)
- การดีพลอย Leptos ไปยัง[รันไทม์แบบเซิร์ฟเวอร์เลส](#การดีพลอยไปยังรันไทมแบบเซิรฟเวอรเลส) - ตัวอย่างเช่น [AWS Lambda](#aws-lambda) และ [รันไทม์ WASM ที่โฮสต์ด้วย JS อย่าง Deno & Cloudflare](#deno--cloudflare-workers)
- [แพลตฟอร์มที่ยังไม่ได้รับการรองรับ Leptos SSR](#แพลตฟอรมทีกำลังพัฒนาการรองรับ-leptos)

_หมายเหตุ: Leptos ไม่ได้ให้การรับรองหรือผูกขาดกับวิธีการดีพลอยหรือบริการโฮสติ้งรายใดรายหนึ่งเป็นพิเศษ_

## การสร้าง Containerfile

วิธีที่นิยมมากที่สุดในการดีพลอยแอปฟูลสแตกที่สร้างด้วย `cargo-leptos` คือการใช้บริการโฮสติ้งบนคลาวด์ที่รองรับการบิลด์และดีพลอยผ่าน Podman หรือ Docker ด้านล่างนี้คือตัวอย่าง `Containerfile` / `Dockerfile` ซึ่งอิงจากไฟล์ที่เราใช้จริงในการดีพลอยเว็บไซต์ Leptos

### Debian

```dockerfile
# Get started with a build env with Rust nightly
FROM rustlang/rust:nightly-trixie as builder

# If you’re using stable, use this instead
# FROM rust:1.92.0-trixie as builder # See current official Rust tags here: https://hub.docker.com/_/rust

# Install cargo-binstall, which makes it easier to install other
# cargo extensions like cargo-leptos
RUN wget https://github.com/cargo-bins/cargo-binstall/releases/latest/download/cargo-binstall-x86_64-unknown-linux-musl.tgz
RUN tar -xvf cargo-binstall-x86_64-unknown-linux-musl.tgz
RUN cp cargo-binstall /usr/local/cargo/bin

# Install required tools
RUN apt-get update -y \
  && apt-get install -y --no-install-recommends clang

# Install cargo-leptos
RUN cargo binstall cargo-leptos -y

# Add the WASM target
RUN rustup target add wasm32-unknown-unknown

# Make an /app dir, which everything will eventually live in
RUN mkdir -p /app
WORKDIR /app
COPY . .

# Build the app
RUN cargo leptos build --release -vv

FROM debian:trixie-slim as runtime
WORKDIR /app
RUN apt-get update -y \
  && apt-get install -y --no-install-recommends openssl ca-certificates \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/*

# -- NB: update binary name from "leptos_start" to match your app name in Cargo.toml --
# Copy the server binary to the /app directory
COPY --from=builder /app/target/release/leptos_start /app/

# /target/site contains our JS/WASM/CSS, etc.
COPY --from=builder /app/target/site /app/site

# Copy Cargo.toml if it’s needed at runtime
COPY --from=builder /app/Cargo.toml /app/

# Set any required env variables and
ENV RUST_LOG="info"
ENV LEPTOS_SITE_ADDR="0.0.0.0:8080"
ENV LEPTOS_SITE_ROOT="site"
EXPOSE 8080

# -- NB: update binary name from "leptos_start" to match your app name in Cargo.toml --
# Run the server
CMD ["/app/leptos_start"]
```

### Alpine

```dockerfile
# Get started with a build env with Rust nightly
FROM rustlang/rust:nightly-alpine as builder

RUN apk update && \
    apk add --no-cache bash curl npm libc-dev binaryen

RUN npm install -g sass

RUN curl --proto '=https' --tlsv1.3 -LsSf https://github.com/leptos-rs/cargo-leptos/releases/latest/download/cargo-leptos-installer.sh | sh

# Add the WASM target
RUN rustup target add wasm32-unknown-unknown

WORKDIR /work
COPY . .

RUN cargo leptos build --release -vv

FROM rustlang/rust:nightly-alpine as runner

WORKDIR /app

COPY --from=builder /work/target/release/leptos_start /app/
COPY --from=builder /work/target/site /app/site
COPY --from=builder /work/Cargo.toml /app/

ENV RUST_LOG="info"
ENV LEPTOS_SITE_ADDR="0.0.0.0:8080"
ENV LEPTOS_SITE_ROOT=./site
EXPOSE 8080

CMD ["/app/leptos_start"]
```

> อ่านเพิ่มเติม: [ไฟล์บิลด์ `gnu` และ `musl` สำหรับแอป Leptos](https://github.com/leptos-rs/leptos/issues/1152#issuecomment-1634916088)

## หมายเหตุเกี่ยวกับรีเวิร์สพร็อกซี

แม้ว่าคุณจะเปิดให้เข้าถึงแอป Leptos ของคุณโดยตรงได้ แต่โดยปกติแล้วการวางไว้เบื้องหลังรีเวิร์สพร็อกซีจะดีกว่า วิธีนี้ช่วยให้คุณจัดการ SSL/TLS การบีบอัด และเฮดเดอร์ด้านความปลอดภัยในเลเยอร์เฉพาะ แทนที่จะทำในไบนารี Rust ของคุณ

มีตัวเลือกรีเวิร์สพร็อกซียอดนิยมอยู่หลายตัว Caddy มักถูกเลือกใช้เพราะจัดการใบรับรอง HTTPS โดยอัตโนมัติ ส่วน Nginx, Traefik หรือ Apache ก็ถูกใช้กันอย่างแพร่หลายเช่นกัน ขึ้นอยู่กับความต้องการและความคุ้นเคยของคุณ

หากคุณใช้ Caddy การกำหนดค่าของคุณก็ง่ายเพียงแค่ชี้โดเมนไปยังชื่อคอนเทนเนอร์หรือ IP ของคุณ:

```Caddyfile
# Simple setup
example.com {
    reverse_proxy leptos-app:8080
}

# Advanced: Basic auth and HSTS headers
app.example.com {
    # Protect a staging site with basic auth
    basic_auth {
        admin $2a$14$CIW9S... 
    }
    
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    }

    reverse_proxy leptos-app:8080
}
```
สำหรับรายละเอียดเพิ่มเติม ดู[คู่มือเริ่มต้นอย่างรวดเร็วสำหรับรีเวิร์สพร็อกซีของ Caddy](https://caddyserver.com/docs/quick-starts/reverse-proxy) และ[เอกสารแนวคิด Caddyfile](https://caddyserver.com/docs/caddyfile) รวมถึงแหล่งข้อมูลอื่นๆ

## การดีพลอยบนคลาวด์

### การดีพลอยไปยัง Fly.io

ทางเลือกหนึ่งสำหรับการดีพลอยแอป Leptos SSR คือการใช้บริการอย่าง [Fly.io](https://fly.io/) ซึ่งจะนำ Dockerfile ของแอป Leptos ไปรันใน micro-VM ที่สตาร์ตได้อย่างรวดเร็ว นอกจากนี้ Fly ยังมีตัวเลือกพื้นที่จัดเก็บข้อมูลและฐานข้อมูลที่มีการจัดการ (managed DB) หลากหลายรูปแบบสำหรับโปรเจกต์ของคุณ ตัวอย่างต่อไปนี้จะแสดงวิธีดีพลอยแอปเริ่มต้นของ Leptos เพื่อให้คุณเริ่มต้นใช้งานได้อย่างรวดเร็ว ([ดูข้อมูลเพิ่มเติมเกี่ยวกับการจัดเก็บข้อมูลบน Fly.io ได้ที่นี่](https://fly.io/docs/database-storage-guides/))

ขั้นตอนแรก ให้สร้างไฟล์ `Dockerfile` ไว้ที่รูทของโปรเจกต์ แล้วใส่เนื้อหาตามตัวอย่างที่แนะนำไว้ด้านบน (อย่าลืมเปลี่ยนชื่อไบนารีให้ตรงกับชื่อแอปของคุณใน `Cargo.toml` และปรับแต่งส่วนอื่น ๆ ตามความเหมาะสม)

จากนั้น ตรวจสอบให้แน่ใจว่าได้ติดตั้งเครื่องมือ CLI `flyctl` และมีบัญชี [Fly.io](https://fly.io/) เรียบร้อยแล้ว สำหรับการติดตั้ง `flyctl` บน macOS, Linux หรือ Windows WSL ให้รันคำสั่ง:

```sh
curl -L https://fly.io/install.sh | sh
```

หากคุณพบปัญหา หรือต้องการติดตั้งบนแพลตฟอร์มอื่น [ดูคำแนะนำฉบับเต็มได้ที่นี่](https://fly.io/docs/hands-on/install-flyctl/)

จากนั้นเข้าสู่ระบบ Fly.io

```sh
fly auth login
```

แล้วเปิดใช้งานแอปของคุณด้วยตนเองด้วยคำสั่ง

```sh
fly launch
```

เครื่องมือ CLI `flyctl` จะพาคุณผ่านกระบวนการดีพลอยแอปของคุณไปยัง Fly.io

```admonish note
โดยค่าเริ่มต้น Fly.io จะหยุดการทำงานของเครื่อง (auto-stop) เมื่อไม่มีทราฟฟิกเข้ามาเป็นระยะเวลาหนึ่ง แม้ว่า micro-VM ของ Fly.io จะสตาร์ตได้เร็วมาก แต่หากคุณต้องการลด latency ของแอป Leptos และต้องการให้ตอบสนองได้ทันทีตลอดเวลา ให้เปิดไฟล์ `fly.toml` ที่ถูกสร้างขึ้น แล้วเปลี่ยนค่า `min_machines_running` จากค่าเริ่มต้น 0 เป็น 1

[ดูหน้านี้ในเอกสารของ Fly.io สำหรับรายละเอียดเพิ่มเติม](https://fly.io/docs/apps/autostart-stop/)
```

หากคุณต้องการใช้ GitHub Actions ในการจัดการการดีพลอย คุณจะต้องสร้าง access token ขึ้นมาใหม่ผ่านหน้าเว็บคอนโซลของ [Fly.io](https://fly.io/)

ไปที่ "Account" > "Access Tokens" แล้วสร้างโทเคน เช่น ตั้งชื่อว่า "github_actions" จากนั้นนำโทเคนดังกล่าวไปเพิ่มใน Secrets ของคลัง GitHub ของคุณ โดยไปที่ GitHub repo ของโปรเจกต์ -> "Settings" -> "Secrets and Variables" -> "Actions" แล้วสร้าง "New repository secret" ชื่อ "FLY_API_TOKEN"

สำหรับการสร้างไฟล์คอนฟิก `fly.toml` ให้รันคำสั่งต่อไปนี้จากไดเรกทอรีโปรเจกต์:

```sh
fly launch --no-deploy
```

เพื่อสร้างและลงทะเบียนแอปใหม่กับบริการ Fly จากนั้นให้คอมมิตไฟล์ `fly.toml` ที่สร้างขึ้นนี้เข้า Git

ในการตั้งค่าเวิร์กโฟลว์การดีพลอยของ Github Actions ให้คัดลอกสิ่งต่อไปนี้ไปยังไฟล์ `.github/workflows/fly_deploy.yml`:

```admonish example collapsible=true

	# For more details, see: https://fly.io/docs/app-guides/continuous-deployment-with-github-actions/

	name: Deploy to Fly.io
	on:
	push:
		branches:
		- main
	jobs:
	deploy:
		name: Deploy app
		runs-on: ubuntu-latest
		steps:
		- uses: actions/checkout@v4
		- uses: superfly/flyctl-actions/setup-flyctl@master
		- name: Deploy to fly
			id: deployment
			run: |
			  flyctl deploy --remote-only | tail -n 1 >> $GITHUB_STEP_SUMMARY
			env:
			  FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

```

เมื่อคุณคอมมิตและพุชโค้ดไปยังแบรนช์ `main` บน GitHub ครั้งถัดไป โปรเจกต์ก็จะถูกดีพลอยขึ้น Fly.io โดยอัตโนมัติ

ดู[รีโพตัวอย่างได้ที่นี่](https://github.com/diversable/fly-io-leptos-ssr-test-deploy)

### Railway

ผู้ให้บริการอีกรายหนึ่งสำหรับการดีพลอยบนคลาวด์คือ [Railway](https://railway.app/)
Railway ผสานรวมกับ GitHub เพื่อดีพลอยโค้ดของคุณโดยอัตโนมัติ

มีเทมเพลตจากชุมชนที่พร้อมให้คุณเริ่มต้นใช้งานได้อย่างรวดเร็ว:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/pduaM5?referralCode=fZ-SY1)

เทมเพลตนี้ตั้งค่า Renovate ไว้เพื่อคอยอัปเดต dependency ให้เป็นเวอร์ชันใหม่อยู่เสมอ และรองรับ GitHub Actions เพื่อทดสอบโค้ดของคุณก่อนจะเริ่มดีพลอยจริง

Railway มีแพ็กเกจฟรีที่ไม่ต้องผูกบัตรเครดิต และเนื่องจาก Leptos ใช้ทรัพยากรน้อยมาก แพ็กเกจฟรีนี้จึงสามารถใช้งานได้ยาวนาน

ดู[รีโพตัวอย่างได้ที่นี่](https://github.com/marvin-bitterlich/leptos-railway)

## การดีพลอยไปยังรันไทม์แบบเซิร์ฟเวอร์เลส

Leptos รองรับการดีพลอยไปยังรันไทม์แบบ FaaS (Function as a Service) หรือ 'serverless' เช่น AWS Lambda รวมถึงรันไทม์ JS ที่รองรับมาตรฐาน [WinterCG](https://wintercg.org/) เช่น [Deno](https://deno.com/deploy) และ Cloudflare ทั้งนี้โปรดทราบว่าสภาพแวดล้อมแบบ serverless จะมีข้อจำกัดบางประการต่อฟังก์ชันการทำงานของแอป SSR เมื่อเทียบกับการดีพลอยบน VM หรือคอนเทนเนอร์ทั่วไป (ดูรายละเอียดด้านล่าง)

### AWS Lambda

ด้วยความช่วยเหลือจากเครื่องมือ [Cargo Lambda](https://www.cargo-lambda.info/) คุณสามารถดีพลอยแอป Leptos SSR ไปยัง AWS Lambda ได้อย่างง่ายดาย มีเทมเพลตเริ่มต้นที่ใช้ Axum อยู่ที่ [leptos-rs/start-aws](https://github.com/leptos-rs/start-aws) (ซึ่งสามารถนำคำแนะนำไปปรับใช้กับ Leptos + Actix-web ได้เช่นกัน) คลังเริ่มต้นนี้มีสคริปต์ GitHub Actions สำหรับ CI/CD พร้อมคำแนะนำในการตั้งค่าฟังก์ชัน Lambda และการขอสิทธิ์ (credentials) สำหรับดีพลอยขึ้นคลาวด์

อย่างไรก็ดี โปรดระลึกไว้ว่าความสามารถบางอย่างของเซิร์ฟเวอร์แบบเนทีฟจะไม่สามารถทำงานบนบริการ FaaS อย่าง Lambda ได้ เนื่องจากสภาพแวดล้อมไม่ได้รับประกันความต่อเนื่องระหว่างแต่ละคำขอ (request) ดังที่ [เอกสาร 'start-aws'](https://github.com/leptos-rs/start-aws#state) ระบุไว้ว่า "เนื่องจาก AWS Lambda เป็นแพลตฟอร์มแบบ serverless คุณจึงต้องระมัดระวังในการจัดการสถานะที่มีอายุยาวนาน (long-lived state) เป็นพิเศษ การเขียนไฟล์ลงดิสก์หรือการใช้ state extractor จะทำงานข้ามคำขอได้อย่างไม่น่าเชื่อถือ คุณจำเป็นต้องใช้ฐานข้อมูลหรือ microservice ภายนอกที่คิวรีได้จากฟังก์ชัน Lambda แทน"

อีกปัจจัยที่ต้องพิจารณาคือเวลา 'cold-start' ของฟังก์ชัน FaaS ซึ่งอาจส่งผลต่อข้อกำหนดด้าน latency ตามแต่กรณีการใช้งานและแพลตฟอร์มที่คุณเลือก คุณอาจจำเป็นต้องตั้งค่าให้มีฟังก์ชันรันเตรียมพร้อมไว้ตลอดเวลาเพื่อเพิ่มความเร็วในการตอบสนองต่อคำขอให้เหมาะสมที่สุด

### Deno & Cloudflare Workers

ปัจจุบัน Leptos-Axum รองรับการรันบนรันไทม์ WebAssembly ที่โฮสต์ด้วย JavaScript เช่น Deno และ Cloudflare Workers ทางเลือกนี้จำเป็นต้องปรับแต่งการตั้งค่าโปรเจกต์เล็กน้อย (เช่น ใน `Cargo.toml` ต้องกำหนดแอปเป็น `crate-type = ["cdylib"]` และเปิดใช้งานฟีเจอร์ "wasm" ของ `leptos_axum`) โดย [ตัวอย่าง Leptos HackerNews JS-fetch](https://github.com/leptos-rs/leptos/tree/leptos_0.6/examples/hackernews_js_fetch) ได้สาธิตการปรับแต่งที่จำเป็นและวิธีรันแอปบน Deno ไว้ นอกจากนี้ [เอกสารประกอบของเครต `leptos_axum`](https://docs.rs/leptos_axum/latest/leptos_axum/#js-fetch-integration) ยังเป็นแหล่งอ้างอิงที่มีประโยชน์มากเมื่อคุณกำหนดค่า `Cargo.toml` ด้วยตนเองสำหรับรันไทม์ WASM ที่โฮสต์ด้วย JS

แม้การตั้งค่าเริ่มต้นสำหรับรันไทม์ WASM ที่โฮสต์ด้วย JS จะไม่ซับซ้อน แต่ข้อจำกัดสำคัญที่ต้องคำนึงถึงคือ แอปจะถูกคอมไพล์เป็น WebAssembly (`wasm32-unknown-unknown`) ทั้งฝั่งเซิร์ฟเวอร์และฝั่งไคลเอนต์ คุณจึงต้องตรวจสอบว่าทุกเครตที่เรียกใช้ในแอปสามารถคอมไพล์ลง WASM ได้ทั้งหมด ซึ่งอาจเป็นอุปสรรคหรือไม่ขึ้นอยู่กับความต้องการของแอป เพราะเครตใน ecosystem ของ Rust ไม่ได้รองรับ WASM ครบทุกตัว

หากคุณยอมรับข้อจำกัดของ WASM ฝั่งเซิร์ฟเวอร์ได้ จุดเริ่มต้นที่ดีที่สุดคือการศึกษาจาก [ตัวอย่างการรัน Leptos ร่วมกับ Deno](https://github.com/leptos-rs/leptos/tree/leptos_0.6/examples/hackernews_js_fetch) ในคลัง GitHub ทางการของ Leptos

## แพลตฟอร์มที่กำลังพัฒนาการรองรับ Leptos

### การดีพลอยไปยัง Spin Serverless WASI (ด้วย Leptos SSR)

ช่วงหลังมานี้ WebAssembly บนฝั่งเซิร์ฟเวอร์เริ่มได้รับความสนใจมากขึ้นเรื่อย ๆ และทีมพัฒนาเฟรมเวิร์ก Spin ซึ่งเป็นโอเพนซอร์ส serverless WebAssembly กำลังพัฒนาการรองรับ Leptos แบบเนทีฟ แม้ว่าการผสานรวมระหว่าง Leptos และ Spin สำหรับ SSR จะยังอยู่ในช่วงเริ่มต้น แต่ก็มีตัวอย่างที่ใช้งานได้จริงให้คุณได้ทดลองแล้ว

คุณสามารถอ่านคำแนะนำฉบับเต็มในการทำให้ Leptos SSR และ Spin ทำงานร่วมกันได้จาก [บล็อกโพสต์ของ Fermyon](https://www.fermyon.com/blog/leptos-spin-get-started) หรือหากต้องการเริ่มต้นทดลองกับเทมเพลตเริ่มต้นที่ใช้งานได้ทันที [สามารถดูได้ที่นี่](https://github.com/diversable/leptos-spin-ssr-test)

### การดีพลอยไปยัง Shuttle.rs

ผู้ใช้ Leptos หลายท่านสอบถามถึงความเป็นไปได้ในการใช้บริการ [Shuttle.rs](https://www.shuttle.rs/) ซึ่งเป็นมิตรกับ Rust เพื่อดีพลอยแอป Leptos แต่น่าเสียดายที่ในขณะนี้ Shuttle.rs ยังไม่รองรับ Leptos อย่างเป็นทางการ

อย่างไรก็ดี ทีมงานของ Shuttle.rs มุ่งมั่นที่จะรองรับ Leptos ในอนาคต หากคุณต้องการติดตามความคืบหน้า สามารถดูได้ที่ [GitHub issue นี้](https://github.com/shuttle-hq/shuttle/issues/1002#issuecomment-1853661643)

นอกจากนี้ ยังมีความพยายามของชุมชนในการทำให้ Shuttle ใช้งานร่วมกับ Leptos ได้ แต่จนถึงปัจจุบัน การดีพลอยขึ้นคลาวด์จริงของ Shuttle ยังไม่ทำงานตามที่คาดหวัง หากคุณต้องการศึกษาด้วยตนเองหรือร่วมส่งการแก้ไข สามารถดูได้ที่: [เทมเพลตเริ่มต้น Leptos Axum สำหรับ Shuttle.rs](https://github.com/Rust-WASI-WASM/shuttle-leptos-axum)
