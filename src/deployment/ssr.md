# การดีพลอยแอป SSR แบบฟูลสแตก

คุณสามารถดีพลอยแอป Leptos แบบฟูลสแตกที่ใช้ SSR ไปยังบริการโฮสติ้งแบบเซิร์ฟเวอร์หรือคอนเทนเนอร์ใดก็ได้ตามต้องการ วิธีที่ง่ายที่สุดในการนำแอป Leptos SSR ขึ้นโปรดักชันอาจเป็นการใช้บริการ VPS แล้วรัน Leptos แบบเนทีฟใน VM ([ดูรายละเอียดเพิ่มเติมได้ที่นี่](https://github.com/leptos-rs/start-axum?tab=readme-ov-file#executing-a-server-on-a-remote-machine-without-the-toolchain)) อีกทางหนึ่ง คุณอาจบรรจุแอป Leptos ของคุณลงคอนเทนเนอร์แล้วรันใน [Podman](https://podman.io/) หรือ [Docker](https://www.docker.com/) บนเซิร์ฟเวอร์แบบโคโลเคชันหรือคลาวด์ใดก็ได้

มีการตั้งค่าการดีพลอยและบริการโฮสติ้งที่แตกต่างกันมากมาย และโดยทั่วไปแล้ว Leptos เองไม่ผูกติดกับการตั้งค่าการดีพลอยที่คุณใช้ ด้วยความหลากหลายของเป้าหมายการดีพลอยนี้ ในหน้านี้เราจะพูดถึง:

- [การสร้าง `Containerfile` (หรือ `Dockerfile`) สำหรับใช้กับแอป Leptos SSR](#การสราง-containerfile)
- การใช้ `Dockerfile` เพื่อ[ดีพลอยไปยังบริการคลาวด์](#การดีพลอยบนคลาวด) - [ตัวอย่างเช่น Fly.io](#การดีพลอยไปยัง-flyio)
- การดีพลอย Leptos ไปยัง[รันไทม์แบบเซิร์ฟเวอร์เลส](#การดีพลอยไปยังรันไทมแบบเซิรฟเวอรเลส) - ตัวอย่างเช่น [AWS Lambda](#aws-lambda) และ [รันไทม์ WASM ที่โฮสต์ด้วย JS อย่าง Deno & Cloudflare](#deno--cloudflare-workers)
- [แพลตฟอร์มที่ยังไม่ได้รับการรองรับ Leptos SSR](#แพลตฟอรมทีกำลังพัฒนาการรองรับ-leptos)

_หมายเหตุ: Leptos ไม่ได้สนับสนุนวิธีการดีพลอยหรือบริการโฮสติ้งใดเป็นการเฉพาะ_

## การสร้าง Containerfile

วิธีที่ผู้คนนิยมใช้มากที่สุดในการดีพลอยแอปฟูลสแตกที่สร้างด้วย `cargo-leptos` คือการใช้บริการโฮสติ้งบนคลาวด์ที่รองรับการดีพลอยผ่านบิลด์ด้วย Podman หรือ Docker นี่คือตัวอย่าง `Containerfile` / `Dockerfile` ซึ่งอ้างอิงจากไฟล์ที่เราใช้ดีพลอยเว็บไซต์ Leptos

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

ทางเลือกหนึ่งสำหรับการดีพลอยแอป Leptos SSR ของคุณคือการใช้บริการอย่าง [Fly.io](https://fly.io/) ซึ่งรับนิยาม Dockerfile ของแอป Leptos ของคุณแล้วรันในไมโคร-VM ที่เริ่มทำงานได้อย่างรวดเร็ว; Fly ยังมีตัวเลือกพื้นที่จัดเก็บและฐานข้อมูลแบบจัดการ (managed DB) หลากหลายให้ใช้กับโปรเจกต์ของคุณ ตัวอย่างต่อไปนี้จะแสดงวิธีดีพลอยแอปเริ่มต้น Leptos ง่ายๆ เพียงเพื่อให้คุณเริ่มต้นใช้งานได้; [ดูที่นี่สำหรับข้อมูลเพิ่มเติมเกี่ยวกับการทำงานกับตัวเลือกพื้นที่จัดเก็บบน Fly.io](https://fly.io/docs/database-storage-guides/) เมื่อคุณต้องการ

อย่างแรก ให้สร้าง `Dockerfile` ในรูทของแอปพลิเคชันของคุณแล้วเติมเนื้อหาตามที่แนะนำ (ด้านบน); อย่าลืมอัปเดตชื่อไบนารีในตัวอย่าง Dockerfile ให้เป็นชื่อแอปพลิเคชันของคุณเอง และปรับเปลี่ยนอย่างอื่นตามความจำเป็น

นอกจากนี้ ตรวจสอบให้แน่ใจว่าคุณได้ติดตั้งเครื่องมือ CLI `flyctl` แล้ว และมีบัญชีที่ตั้งค่าไว้ที่ [Fly.io](https://fly.io/) ในการติดตั้ง `flyctl` บน MacOS, Linux หรือ Windows WSL ให้รัน:

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
โดยค่าเริ่มต้น Fly.io จะหยุดเครื่องที่ไม่มีทราฟฟิกเข้ามาโดยอัตโนมัติหลังจากผ่านไประยะเวลาหนึ่ง แม้ว่าไมโคร-VM ของ Fly.io จะเริ่มทำงานได้อย่างรวดเร็ว แต่หากคุณต้องการลดเวลาแฝงของแอป Leptos และมั่นใจว่ามันตอบสนองได้อย่างรวดเร็วเสมอ ให้เปิดไฟล์ `fly.toml` ที่สร้างขึ้นแล้วเปลี่ยน `min_machines_running` จากค่าเริ่มต้น 0 เป็น 1

[ดูหน้านี้ในเอกสารของ Fly.io สำหรับรายละเอียดเพิ่มเติม](https://fly.io/docs/apps/autostart-stop/).
```

หากคุณต้องการใช้ Github Actions ในการจัดการการดีพลอยของคุณ คุณจะต้องสร้างโทเคนการเข้าถึงใหม่ผ่านส่วนติดต่อผู้ใช้เว็บของ [Fly.io](https://fly.io/)

ไปที่ "Account" > "Access Tokens" แล้วสร้างโทเคนชื่อประมาณ "github_actions" จากนั้นเพิ่มโทเคนนั้นลงใน secrets ของรีโพ Github ของคุณ โดยไปที่รีโพ Github ของโปรเจกต์คุณ แล้วคลิก "Settings" > "Secrets and Variables" > "Actions" และสร้าง "New repository secret" ด้วยชื่อ "FLY_API_TOKEN"

ในการสร้างไฟล์กำหนดค่า `fly.toml` สำหรับการดีพลอยไปยัง Fly.io คุณต้องรันคำสั่งต่อไปนี้จากภายในไดเรกทอรีซอร์สของโปรเจกต์ก่อน

```sh
fly launch --no-deploy
```

เพื่อสร้างแอป Fly ใหม่และลงทะเบียนกับบริการ จากนั้นคอมมิตไฟล์ `fly.toml` ใหม่ของคุณด้วย Git

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

เมื่อมีการคอมมิตครั้งถัดไปไปยังแบรนช์ `main` บน Github โปรเจกต์ของคุณจะดีพลอยไปยัง Fly.io โดยอัตโนมัติ

ดู[รีโพตัวอย่างได้ที่นี่](https://github.com/diversable/fly-io-leptos-ssr-test-deploy)

### Railway

ผู้ให้บริการอีกรายหนึ่งสำหรับการดีพลอยบนคลาวด์คือ [Railway](https://railway.app/)
Railway ผสานรวมกับ GitHub เพื่อดีพลอยโค้ดของคุณโดยอัตโนมัติ

มีเทมเพลตจากชุมชนที่กำหนดแนวทางไว้อย่างชัดเจนซึ่งช่วยให้คุณเริ่มต้นได้อย่างรวดเร็ว:

[![ดีพลอยบน Railway](https://railway.app/button.svg)](https://railway.app/template/pduaM5?referralCode=fZ-SY1)

เทมเพลตนี้ตั้งค่า renovate ไว้เพื่อให้ดีเพนเดนซีเป็นปัจจุบันอยู่เสมอ และรองรับ GitHub Actions สำหรับทดสอบโค้ดของคุณก่อนที่จะมีการดีพลอย

Railway มีแพ็กเกจฟรีที่ไม่ต้องใช้บัตรเครดิต และด้วยทรัพยากรที่ Leptos ต้องการนั้นน้อยมาก แพ็กเกจฟรีนี้จึงน่าจะใช้งานได้นาน

ดู[รีโพตัวอย่างได้ที่นี่](https://github.com/marvin-bitterlich/leptos-railway)

## การดีพลอยไปยังรันไทม์แบบเซิร์ฟเวอร์เลส

Leptos รองรับการดีพลอยไปยังรันไทม์แบบ FaaS (Function as a Service) หรือ 'เซิร์ฟเวอร์เลส' อย่าง AWS Lambda รวมถึงรันไทม์ JS ที่เข้ากันได้กับ [WinterCG](https://wintercg.org/) อย่าง [Deno](https://deno.com/deploy) และ Cloudflare เพียงโปรดทราบว่าสภาพแวดล้อมแบบเซิร์ฟเวอร์เลสมีข้อจำกัดบางประการต่อฟังก์ชันการทำงานที่ใช้ได้กับแอป SSR ของคุณ เมื่อเทียบกับการดีพลอยแบบ VM หรือคอนเทนเนอร์ (ดูหมายเหตุด้านล่าง)

### AWS Lambda

ด้วยความช่วยเหลือเล็กน้อยจากเครื่องมือ [Cargo Lambda](https://www.cargo-lambda.info/) แอป Leptos SSR สามารถถูกดีพลอยไปยัง AWS Lambda ได้ รีโพเทมเพลตเริ่มต้นที่ใช้ Axum เป็นเซิร์ฟเวอร์มีอยู่ที่ [leptos-rs/start-aws](https://github.com/leptos-rs/start-aws); คำแนะนำในนั้นสามารถดัดแปลงให้คุณใช้เซิร์ฟเวอร์ Leptos+Actix-web ได้เช่นกัน รีโพเริ่มต้นนี้มีสคริปต์ Github Actions สำหรับ CI/CD รวมถึงคำแนะนำในการตั้งค่าฟังก์ชัน Lambda และการขอข้อมูลรับรองที่จำเป็นสำหรับการดีพลอยบนคลาวด์

อย่างไรก็ตาม โปรดจำไว้ว่าฟังก์ชันการทำงานบางอย่างของเซิร์ฟเวอร์แบบเนทีฟไม่สามารถใช้ได้กับบริการ FaaS อย่าง Lambda เพราะสภาพแวดล้อมไม่จำเป็นต้องสอดคล้องกันจากคำขอหนึ่งไปยังคำขอถัดไป โดยเฉพาะอย่างยิ่ง [เอกสาร 'start-aws'](https://github.com/leptos-rs/start-aws#state) ระบุว่า "เนื่องจาก AWS Lambda เป็นแพลตฟอร์มแบบเซิร์ฟเวอร์เลส คุณจะต้องระมัดระวังมากขึ้นในการจัดการสถานะที่มีอายุยาวนาน การเขียนลงดิสก์หรือการใช้เอกซ์แทรกเตอร์สถานะจะไม่ทำงานอย่างเชื่อถือได้ในแต่ละคำขอ แต่คุณจะต้องใช้ฐานข้อมูลหรือไมโครเซอร์วิสอื่นๆ ที่คุณสามารถคิวรีได้จากฟังก์ชัน Lambda"

อีกปัจจัยหนึ่งที่ควรคำนึงถึงคือเวลา 'คอลด์สตาร์ท' ของฟังก์ชันแบบบริการ - ขึ้นอยู่กับกรณีการใช้งานและแพลตฟอร์ม FaaS ที่คุณใช้ สิ่งนี้อาจเข้าเกณฑ์ความต้องการด้านเวลาแฝงของคุณหรือไม่ก็ได้; คุณอาจต้องให้ฟังก์ชันหนึ่งทำงานตลอดเวลาเพื่อปรับความเร็วของคำขอของคุณให้เหมาะสมที่สุด

### Deno & Cloudflare Workers

ปัจจุบัน Leptos-Axum รองรับการทำงานในรันไทม์ WebAssembly ที่โฮสต์ด้วย Javascript อย่าง Deno, Cloudflare Workers ฯลฯ ทางเลือกนี้ต้องมีการเปลี่ยนแปลงการตั้งค่าซอร์สโค้ดของคุณบ้าง (ตัวอย่างเช่น ใน `Cargo.toml` คุณต้องนิยามแอปของคุณด้วย `crate-type = ["cdylib"]` และต้องเปิดใช้งานฟีเจอร์ "wasm" สำหรับ `leptos_axum`) [ตัวอย่าง Leptos HackerNews JS-fetch](https://github.com/leptos-rs/leptos/tree/leptos_0.6/examples/hackernews_js_fetch) สาธิตการปรับเปลี่ยนที่จำเป็นและแสดงวิธีรันแอปในรันไทม์ Deno นอกจากนี้ [เอกสารของครีต `leptos_axum`](https://docs.rs/leptos_axum/latest/leptos_axum/#js-fetch-integration) ยังเป็นเอกสารอ้างอิงที่มีประโยชน์เมื่อคุณตั้งค่าไฟล์ `Cargo.toml` ของคุณเองสำหรับรันไทม์ WASM ที่โฮสต์ด้วย JS

แม้ว่าการตั้งค่าเริ่มต้นสำหรับรันไทม์ WASM ที่โฮสต์ด้วย JS จะไม่ยุ่งยากนัก แต่ข้อจำกัดที่สำคัญกว่าที่ควรจำไว้คือ เนื่องจากแอปของคุณจะถูกคอมไพล์เป็น WebAssembly (`wasm32-unknown-unknown`) ทั้งบนเซิร์ฟเวอร์และไคลเอนต์ คุณจึงต้องมั่นใจว่าครีตทั้งหมดที่คุณใช้ในแอปนั้นรองรับ WASM; สิ่งนี้อาจเป็นหรือไม่เป็นอุปสรรคสำคัญก็ได้ ขึ้นอยู่กับความต้องการของแอปของคุณ เพราะไม่ใช่ทุกครีตในระบบนิเวศ Rust ที่รองรับ WASM

หากคุณยอมรับข้อจำกัดของ WASM ฝั่งเซิร์ฟเวอร์ได้ ที่ที่ดีที่สุดในการเริ่มต้นตอนนี้คือการดู[ตัวอย่างการรัน Leptos กับ Deno](https://github.com/leptos-rs/leptos/tree/leptos_0.6/examples/hackernews_js_fetch) ในรีโพ Github อย่างเป็นทางการของ Leptos

## แพลตฟอร์มที่กำลังพัฒนาการรองรับ Leptos

### การดีพลอยไปยัง Spin Serverless WASI (ด้วย Leptos SSR)

ช่วงหลังนี้ WebAssembly บนเซิร์ฟเวอร์กำลังได้รับความนิยมมากขึ้น และผู้พัฒนาเฟรมเวิร์ก WebAssembly แบบเซิร์ฟเวอร์เลสโอเพนซอร์สอย่าง Spin กำลังพัฒนาการรองรับ Leptos แบบเนทีฟ แม้ว่าการผสานรวม Leptos-Spin สำหรับ SSR จะยังอยู่ในช่วงเริ่มต้น แต่ก็มีตัวอย่างที่ใช้งานได้ซึ่งคุณอาจต้องการลอง

คำแนะนำฉบับเต็มสำหรับการทำให้ Leptos SSR และ Spin ทำงานร่วมกันมีอยู่ใน[โพสต์บนบล็อกของ Fermyon](https://www.fermyon.com/blog/leptos-spin-get-started) หรือหากคุณต้องการข้ามบทความนั้นแล้วเริ่มลองเล่นกับรีโพเริ่มต้นที่ใช้งานได้เลย [ดูที่นี่](https://github.com/diversable/leptos-spin-ssr-test)

### การดีพลอยไปยัง Shuttle.rs

ผู้ใช้ Leptos หลายคนได้สอบถามเกี่ยวกับความเป็นไปได้ในการใช้บริการ [Shuttle.rs](https://www.shuttle.rs/) ที่เป็นมิตรกับ Rust เพื่อดีพลอยแอป Leptos น่าเสียดายที่ในขณะนี้ Leptos ยังไม่ได้รับการรองรับอย่างเป็นทางการจากบริการ Shuttle.rs

อย่างไรก็ตาม ทีมงานที่ Shuttle.rs มุ่งมั่นที่จะรองรับ Leptos ในอนาคต; หากคุณต้องการติดตามความคืบหน้าของงานนี้ โปรดจับตาดู[ประเด็นใน Github นี้](https://github.com/shuttle-hq/shuttle/issues/1002#issuecomment-1853661643)

นอกจากนี้ ยังมีความพยายามบางส่วนในการทำให้ Shuttle ทำงานกับ Leptos แต่จนถึงปัจจุบัน การดีพลอยไปยังคลาวด์ของ Shuttle ก็ยังไม่ทำงานอย่างที่คาดหวัง งานดังกล่าวอยู่ที่นี่ หากคุณต้องการตรวจสอบด้วยตนเองหรือร่วมส่งแพตช์แก้ไข: [เทมเพลตเริ่มต้น Leptos Axum สำหรับ Shuttle.rs](https://github.com/Rust-WASI-WASM/shuttle-leptos-axum)
