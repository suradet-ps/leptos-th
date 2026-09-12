# การจัดเส้นทางแบบซ้อน

เราเพิ่งนิยามชุดเส้นทางต่อไปนี้:

```rust
<Routes fallback=|| "Not found.">
  <Route path=path!("/") view=Home/>
  <Route path=path!("/users") view=Users/>
  <Route path=path!("/users/:id") view=UserProfile/>
  <Route path=path!("/*any") view=|| view! { <h1>"Not Found"</h1> }/>
</Routes>
```

มีความซ้ำซ้อนอยู่พอสมควรตรงนี้: `/users` และ `/users/:id` ซึ่งไม่เป็นปัญหาสำหรับแอปเล็กๆ แต่คุณคงบอกได้แล้วว่ามันจะขยายขนาดได้ไม่ดีนัก จะดีแค่ไหนถ้าเราซ้อนเส้นทางเหล่านี้ได้?

ก็... คุณทำได้!

```rust
<Routes fallback=|| "Not found.">
  <Route path=path!("/") view=Home/>
  <ParentRoute path=path!("/users") view=Users>
    <Route path=path!(":id") view=UserProfile/>
  </ParentRoute>
  <Route path=path!("/*any") view=|| view! { <h1>"Not Found"</h1> }/>
</Routes>
```

คุณซ้อน `<Route/>` ไว้ใน `<ParentRoute/>` ได้ ดูตรงไปตรงมาดี

แต่เดี๋ยวก่อน เราเพิ่งเปลี่ยนสิ่งที่แอปพลิเคชันของเราทำไปอย่างแนบเนียน

หัวข้อถัดไปเป็นหนึ่งในหัวข้อที่สำคัญที่สุดในส่วนว่าด้วยการจัดเส้นทางทั้งหมดของคู่มือนี้ อ่านให้ละเอียด และเชิญถามคำถามได้เลยหากมีอะไรที่คุณไม่เข้าใจ

# เส้นทางแบบซ้อนในฐานะเลย์เอาต์

เส้นทางแบบซ้อนเป็นรูปแบบหนึ่งของเลย์เอาต์ ไม่ใช่วิธีนิยามเส้นทาง

ขอผมพูดอีกอย่างหนึ่ง: เป้าหมายของการนิยามเส้นทางแบบซ้อนไม่ใช่เพื่อหลีกเลี่ยงการเขียนซ้ำเวลาพิมพ์พาธในนิยามเส้นทางของคุณเป็นหลัก อันที่จริงมันคือการบอกเราเตอร์ให้แสดง `<Route/>` หลายตัวบนหน้าเพจในเวลาเดียวกัน เคียงข้างกัน

ลองย้อนกลับไปดูตัวอย่างจริงของเรา

```rust
<Routes fallback=|| "Not found.">
  <Route path=path!("/users") view=Users/>
  <Route path=path!("/users/:id") view=UserProfile/>
</Routes>
```

นี่หมายความว่า:

- หากผมไปที่ `/users` ผมจะได้คอมโพเนนต์ `<Users/>`
- หากผมไปที่ `/users/3` ผมจะได้คอมโพเนนต์ `<UserProfile/>` (โดยพารามิเตอร์ `id` ถูกตั้งเป็น `3`; เดี๋ยวจะพูดถึงในภายหลัง)

สมมติว่าผมใช้เส้นทางแบบซ้อนแทน:

```rust
<Routes fallback=|| "Not found.">
  <ParentRoute path=path!("/users") view=Users>
    <Route path=path!(":id") view=UserProfile/>
  </ParentRoute>
</Routes>
```

นี่หมายความว่า:

- หากผมไปที่ `/users/3` พาธจะตรงกับ `<Route/>` สองตัว: `<Users/>` และ `<UserProfile/>`
- หากผมไปที่ `/users` พาธจะไม่ถูกจับคู่

ที่จริงผมต้องเพิ่มเส้นทางฟอลแบ็ก

```rust
<Routes>
  <ParentRoute path=path!("/users") view=Users>
    <Route path=path!(":id") view=UserProfile/>
    <Route path=path!("") view=NoUser/>
  </ParentRoute>
</Routes>
```

ตอนนี้:

- หากผมไปที่ `/users/3` พาธจะตรงกับ `<Users/>` และ `<UserProfile/>`
- หากผมไปที่ `/users` พาธจะตรงกับ `<Users/>` และ `<NoUser/>`

เมื่อผมใช้เส้นทางแบบซ้อน พูดอีกอย่างคือ แต่ละ**พาธ**สามารถตรงกับ**เส้นทาง**หลายๆ เส้นทางได้: แต่ละ URL สามารถเรนเดอร์วิวที่คอมโพเนนต์ `<Route/>` หลายตัวจัดหาให้ ในเวลาเดียวกัน บนหน้าเพจเดียวกัน

เรื่องนี้อาจขัดกับสัญชาตญาณ แต่มันทรงพลังมาก ด้วยเหตุผลที่คุณคงได้เห็นในอีกไม่กี่นาที

## ทำไมต้องจัดเส้นทางแบบซ้อน?

แล้วจะยุ่งกับเรื่องนี้ทำไม?

เว็บแอปพลิเคชันส่วนใหญ่มีระดับของการนำทางที่สอดคล้องกับส่วนต่างๆ ของเลย์เอาต์ ตัวอย่างเช่น ในแอปอีเมล คุณอาจมี URL อย่าง `/contacts/greg` ซึ่งแสดงรายชื่อผู้ติดต่อทางซ้ายของหน้าจอ และรายละเอียดผู้ติดต่อของ Greg ทางขวาของหน้าจอ รายชื่อผู้ติดต่อและรายละเอียดผู้ติดต่อควรปรากฏบนหน้าจอพร้อมกันเสมอ หากไม่มีผู้ติดต่อที่ถูกเลือก คุณอาจต้องการแสดงข้อความแนะนำสั้นๆ

คุณนิยามสิ่งนี้ได้ง่ายๆ ด้วยเส้นทางแบบซ้อน

```rust
<Routes fallback=|| "Not found.">
  <ParentRoute path=path!("/contacts") view=ContactList>
    <Route path=path!(":id") view=ContactInfo/>
    <Route path=path!("") view=|| view! {
      <p>"Select a contact to view more info."</p>
    }/>
  </ParentRoute>
</Routes>
```

คุณลงลึกได้อีก สมมติว่าคุณต้องการมีแท็บสำหรับที่อยู่ อีเมล/โทรศัพท์ และบทสนทนากับผู้ติดต่อแต่ละคน คุณสามารถเพิ่มเส้นทางแบบซ้อน_อีกชุดหนึ่ง_ไว้ใน `:id`:

```rust
<Routes fallback=|| "Not found.">
  <ParentRoute path=path!("/contacts") view=ContactList>
    <ParentRoute path=path!(":id") view=ContactInfo>
      <Route path=path!("") view=EmailAndPhone/>
      <Route path=path!("address") view=Address/>
      <Route path=path!("messages") view=Messages/>
    </ParentRoute>
    <Route path=path!("") view=|| view! {
      <p>"Select a contact to view more info."</p>
    }/>
  </ParentRoute>
</Routes>
```

> หน้าหลักของ[เว็บไซต์ Remix](https://remix.run/) ซึ่งเป็นเฟรมเวิร์ก React จากผู้สร้าง React Router มีตัวอย่างภาพประกอบที่ยอดเยี่ยมหากคุณเลื่อนลงไป โดยมีเส้นทางแบบซ้อนสามระดับ: Sales > Invoices > ใบแจ้งหนี้หนึ่งใบ

## `<Outlet/>`

เส้นทางแม่ไม่ได้เรนเดอร์เส้นทางแบบซ้อนของมันโดยอัตโนมัติ ยังไงซะ พวกมันก็เป็นแค่คอมโพเนนต์ พวกมันไม่รู้แน่ชัดว่าควรเรนเดอร์ children ของพวกมันตรงไหน และ “ก็แปะไว้ท้ายคอมโพเนนต์แม่สิ” ก็ไม่ใช่คำตอบที่ดีนัก

แต่คุณบอกคอมโพเนนต์แม่ว่าควรเรนเดอร์คอมโพเนนต์แบบซ้อนตรงไหน ด้วยคอมโพเนนต์ `<Outlet/>` โดย `<Outlet/>` จะเรนเดอร์หนึ่งในสองอย่างง่ายๆ:

- หากไม่มีเส้นทางแบบซ้อนที่ถูกจับคู่ มันจะไม่แสดงอะไรเลย
- หากมีเส้นทางแบบซ้อนที่ถูกจับคู่ มันจะแสดง `view` ของเส้นทางนั้น

แค่นั้นเอง! แต่มันสำคัญที่ต้องรู้และจดจำ เพราะมันเป็นสาเหตุที่พบบ่อยของความหงุดหงิดแบบ “ทำไมมันไม่ทำงาน?” หากคุณไม่จัดเตรียม `<Outlet/>` เส้นทางแบบซ้อนจะไม่ถูกแสดง

```rust
#[component]
pub fn ContactList() -> impl IntoView {
  let contacts = todo!();

  view! {
    <div style="display: flex">
      // the contact list
      <For each=contacts
        key=|contact| contact.id
        children=|contact| todo!()
      />
      // the nested child, if any
      // don’t forget this!
      <Outlet/>
    </div>
  }
}
```

## การรีแฟกเตอร์การนิยามเส้นทาง

คุณไม่จำเป็นต้องนิยามเส้นทางทั้งหมดในที่เดียวหากคุณไม่ต้องการ คุณสามารถรีแฟกเตอร์ `<Route/>` ใดๆ และ children ของมันออกไปเป็นคอมโพเนนต์แยกต่างหากได้

ตัวอย่างเช่น คุณสามารถรีแฟกเตอร์ตัวอย่างข้างบนให้ใช้สองคอมโพเนนต์แยกกัน:

```rust
#[component]
pub fn App() -> impl IntoView {
    view! {
      <Router>
        <Routes fallback=|| "Not found.">
          <ParentRoute path=path!("/contacts") view=ContactList>
            <ContactInfoRoutes/>
            <Route path=path!("") view=|| view! {
              <p>"Select a contact to view more info."</p>
            }/>
          </ParentRoute>
        </Routes>
      </Router>
    }
}

#[component(transparent)]
fn ContactInfoRoutes() -> impl MatchNestedRoutes + Clone {
    view! {
      <ParentRoute path=path!(":id") view=ContactInfo>
        <Route path=path!("") view=EmailAndPhone/>
        <Route path=path!("address") view=Address/>
        <Route path=path!("messages") view=Messages/>
      </ParentRoute>
    }
    .into_inner()
    .into_any_nested_route()
}
```

คอมโพเนนต์ที่สองนี้เป็น `#[component(transparent)]` หมายความว่ามันคืนค่าแค่ข้อมูลของมัน ไม่ใช่วิว เช่นเดียวกัน มันใช้ `.into_inner()` เพื่อลบข้อมูลดีบักบางอย่างที่มาโคร `view` เพิ่มเข้ามา และคืนค่าแค่การนิยามเส้นทางที่สร้างโดย `<ParentRoute/>`

## การจัดเส้นทางแบบซ้อนและประสิทธิภาพ

ทั้งหมดนี้ดีในเชิงแนวคิด แต่ถามอีกครั้ง—มันเรื่องใหญ่อะไร?

ประสิทธิภาพ

ในไลบรารีรีแอกทีฟแบบละเอียดอย่าง Leptos สิ่งสำคัญเสมอคือการทำงานเรนเดอร์ให้น้อยที่สุดเท่าที่ทำได้ เพราะเราทำงานกับโหนด DOM จริง ไม่ได้ทำการดิฟฟ์ virtual DOM เราจึงอยาก “เรนเดอร์ใหม่” คอมโพเนนต์ให้น้อยครั้งที่สุดเท่าที่จะเป็นไปได้ การจัดเส้นทางแบบซ้อนทำให้เรื่องนี้ง่ายมาก

ลองนึกภาพตัวอย่างรายชื่อผู้ติดต่อของผม หากผมนำทางจาก Greg ไป Alice ไป Bob แล้วกลับมา Greg ข้อมูลผู้ติดต่อต้องเปลี่ยนในการนำทางแต่ละครั้ง แต่ `<ContactList/>` ไม่ควรถูกเรนเดอร์ใหม่เลย ไม่เพียงแต่ประหยัดประสิทธิภาพการเรนเดอร์เท่านั้น แต่ยังรักษาสถานะใน UI ไว้ด้วย ตัวอย่างเช่น หากผมมีแถบค้นหาที่ด้านบนของ `<ContactList/>` การนำทางจาก Greg ไป Alice ไป Bob จะไม่ล้างการค้นหา

ที่จริง ในกรณีนี้ เราไม่จำเป็นต้องเรนเดอร์คอมโพเนนต์ `<Contact/>` ใหม่ด้วยซ้ำเมื่อย้ายระหว่างผู้ติดต่อ เราเตอร์จะอัปเดตพารามิเตอร์ `:id` อย่างรีแอกทีฟขณะที่เรานำทาง ทำให้เราสามารถทำการอัปเดตแบบละเอียดได้ ขณะที่เรานำทางระหว่างผู้ติดต่อ เราจะอัปเดตโหนดข้อความเดี่ยวเพื่อเปลี่ยนชื่อ ที่อยู่ และอื่นๆ ของผู้ติดต่อ โดยไม่ต้องเรนเดอร์ใหม่เพิ่มเติม_ใดๆ_เลย

> แซนด์บ็อกซ์นี้มีฟีเจอร์สองสามอย่าง (เช่น การจัดเส้นทางแบบซ้อน) ที่อภิปรายกันในหัวข้อนี้และหัวข้อก่อนหน้า และอีกสองสามอย่างที่เราจะพูดถึงในส่วนที่เหลือของบทนี้ เราเตอร์เป็นระบบที่ผสานรวมกันมากจนสมเหตุสมผลที่จะมอบตัวอย่างเดียว ดังนั้นอย่าแปลกใจหากมีอะไรที่คุณไม่เข้าใจ

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox.](https://codesandbox.io/p/devbox/16-router-0-7-csm8t5?file=%2Fsrc%2Fmain.rs)

<noscript>
  กรุณาเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/16-router-0-7-csm8t5?file=%2Fsrc%2Fmain.rs" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;
use leptos_router::components::{Outlet, ParentRoute, Route, Router, Routes, A};
use leptos_router::hooks::use_params_map;
use leptos_router::path;

#[component]
pub fn App() -> impl IntoView {
    view! {
        <Router>
            <h1>"Contact App"</h1>
            // this <nav> will show on every routes,
            // because it's outside the <Routes/>
            // note: we can just use normal <a> tags
            // and the router will use client-side navigation
            <nav>
                <a href="/">"Home"</a>
                <a href="/contacts">"Contacts"</a>
            </nav>
            <main>
                <Routes fallback=|| "Not found.">
                    // / just has an un-nested "Home"
                    <Route path=path!("/") view=|| view! {
                        <h3>"Home"</h3>
                    }/>
                    // /contacts has nested routes
                    <ParentRoute
                        path=path!("/contacts")
                        view=ContactList
                      >
                        // if no id specified, fall back
                        <ParentRoute path=path!(":id") view=ContactInfo>
                            <Route path=path!("") view=|| view! {
                                <div class="tab">
                                    "(Contact Info)"
                                </div>
                            }/>
                            <Route path=path!("conversations") view=|| view! {
                                <div class="tab">
                                    "(Conversations)"
                                </div>
                            }/>
                        </ParentRoute>
                        // if no id specified, fall back
                        <Route path=path!("") view=|| view! {
                            <div class="select-user">
                                "Select a user to view contact info."
                            </div>
                        }/>
                    </ParentRoute>
                </Routes>
            </main>
        </Router>
    }
}

#[component]
fn ContactList() -> impl IntoView {
    view! {
        <div class="contact-list">
            // here's our contact list component itself
            <h3>"Contacts"</h3>
            <div class="contact-list-contacts">
                <A href="alice">"Alice"</A>
                <A href="bob">"Bob"</A>
                <A href="steve">"Steve"</A>
            </div>

            // <Outlet/> will show the nested child route
            // we can position this outlet wherever we want
            // within the layout
            <Outlet/>
        </div>
    }
}

#[component]
fn ContactInfo() -> impl IntoView {
    // we can access the :id param reactively with `use_params_map`
    let params = use_params_map();
    let id = move || params.read().get("id").unwrap_or_default();

    // imagine we're loading data from an API here
    let name = move || match id().as_str() {
        "alice" => "Alice",
        "bob" => "Bob",
        "steve" => "Steve",
        _ => "User not found.",
    };

    view! {
        <h4>{name}</h4>
        <div class="contact-info">
            <div class="tabs">
                <A href="" exact=true>"Contact Info"</A>
                <A href="conversations">"Conversations"</A>
            </div>

            // <Outlet/> here is the tabs that are nested
            // underneath the /contacts/:id route
            <Outlet/>
        </div>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
